// This file was generated with the assistance of an AI coding tool.
/********************************************************************************
 *                                                                              *
 * This file is part of Bonsai.                                                 *
 *                                                                              *
 * Bonsai is free software: you can redistribute it and/or modify               *
 * it under the terms of the GNU General Public License as published by         *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * Bonsai is distributed in the hope that it will be useful,                    *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * GNU General Public License for more details.                                 *
 *                                                                              *
 * You should have received a copy of the GNU General Public License            *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#include "Panel.h"

#include "../../../ifcviewer/ViewportWindow.h"
#include "../models/Commands.h"

#include <QDebug>
#include <QDragEnterEvent>
#include <QDropEvent>
#include <QEvent>
#include <QFrame>
#include <QMimeData>
#include <QPlatformSurfaceEvent>
#include <QVBoxLayout>
#include <QWidget>

#include <string>

#ifdef Q_OS_WIN
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <oleidl.h>
#include <shellapi.h>
#endif

namespace bonsaiviewer::modules::viewport {

namespace {

#ifdef Q_OS_WIN

// <# ************************************************************************************************>
QStringList pathsFromDataObject(IDataObject* data) {
    if (!data) return {};

    FORMATETC format = {};
    format.cfFormat = CF_HDROP;
    format.dwAspect = DVASPECT_CONTENT;
    format.lindex = -1;
    format.tymed = TYMED_HGLOBAL;

    STGMEDIUM medium = {};
    if (FAILED(data->GetData(&format, &medium))) return {};

    QStringList paths;
    auto* drop = static_cast<HDROP>(GlobalLock(medium.hGlobal));
    if (drop) {
        const UINT count = DragQueryFileW(drop, 0xFFFFFFFF, nullptr, 0);
        for (UINT i = 0; i < count; ++i) {
            const UINT length = DragQueryFileW(drop, i, nullptr, 0);
            if (length == 0) continue;
            std::wstring buffer(static_cast<size_t>(length) + 1, L'\0');
            if (DragQueryFileW(drop, i, buffer.data(), length + 1) == 0) continue;
            paths.push_back(QString::fromWCharArray(buffer.c_str()));
        }
        GlobalUnlock(medium.hGlobal);
    }
    ReleaseStgMedium(&medium);
    return modules::models::commands::ifcFilesFromPaths(paths);
}

// Explorer file drops land on the native viewport HWND. Qt never turns those
// into QDropEvents, so the HWND registers its own OLE drop target.
class FileDropTarget : public IDropTarget {
public:
    explicit FileDropTarget(ViewportPanel* panel)
        : panel_(panel) {}

    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void** object) override {
        if (!object) return E_POINTER;
        if (riid == IID_IUnknown || riid == IID_IDropTarget) {
            *object = static_cast<IDropTarget*>(this);
            AddRef();
            return S_OK;
        }
        *object = nullptr;
        return E_NOINTERFACE;
    }

    ULONG STDMETHODCALLTYPE AddRef() override {
        return static_cast<ULONG>(InterlockedIncrement(&ref_));
    }

    ULONG STDMETHODCALLTYPE Release() override {
        const ULONG count = static_cast<ULONG>(InterlockedDecrement(&ref_));
        if (count == 0) delete this;
        return count;
    }

    HRESULT STDMETHODCALLTYPE DragEnter(IDataObject* data, DWORD /*key_state*/, POINTL /*point*/,
                                        DWORD* effect) override {
        pending_paths_ = pathsFromDataObject(data);
        *effect = pending_paths_.isEmpty() ? DROPEFFECT_NONE : DROPEFFECT_COPY;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE DragOver(DWORD /*key_state*/, POINTL /*point*/, DWORD* effect) override {
        *effect = pending_paths_.isEmpty() ? DROPEFFECT_NONE : DROPEFFECT_COPY;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE DragLeave() override {
        pending_paths_.clear();
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE Drop(IDataObject* data, DWORD /*key_state*/, POINTL /*point*/,
                                   DWORD* effect) override {
        QStringList paths = pathsFromDataObject(data);
        if (paths.isEmpty()) paths = pending_paths_;
        pending_paths_.clear();
        *effect = paths.isEmpty() ? DROPEFFECT_NONE : DROPEFFECT_COPY;
        if (!paths.isEmpty() && panel_) panel_->deliverDroppedIfcFiles(paths);
        return S_OK;
    }

private:
    ViewportPanel* panel_ = nullptr;
    QStringList pending_paths_;
    LONG ref_ = 1;
};

#endif

} // namespace

// <# ************************************************************************************************>
ViewportPanel::ViewportPanel(QWidget* parent)
    : QWidget(parent)
{
    auto* root = new QVBoxLayout(this);
    root->setContentsMargins(0, 0, 0, 0);
    root->setSpacing(0);

    auto* shell = new QFrame(this);
    shell->setObjectName("viewportShell");
    auto* shell_layout = new QVBoxLayout(shell);
    shell_layout->setContentsMargins(10, 10, 10, 10);
    shell_layout->setSpacing(0);

    auto* frame = new QFrame(shell);
    frame->setObjectName("viewportFrame");
    auto* frame_layout = new QVBoxLayout(frame);
    frame_layout->setContentsMargins(0, 0, 0, 0);
    frame_layout->setSpacing(0);

    viewport_ = new ViewportWindow();
    viewport_->installEventFilter(this);
    viewport_container_ = QWidget::createWindowContainer(viewport_, frame);
    viewport_container_->setMinimumSize(400, 300);
    viewport_container_->setFocusPolicy(Qt::StrongFocus);
    viewport_container_->setAcceptDrops(true);
    viewport_container_->installEventFilter(this);

    frame_layout->addWidget(viewport_container_);
    shell_layout->addWidget(frame);
    root->addWidget(shell);

#ifdef Q_OS_WIN
    registerNativeFileDrop();
#endif
}

// <# ************************************************************************************************>
ViewportPanel::~ViewportPanel() {
#ifdef Q_OS_WIN
    revokeNativeFileDrop();
#endif
}

// <# ************************************************************************************************>
void ViewportPanel::deliverDroppedIfcFiles(const QStringList& paths) {
    if (paths.isEmpty()) return;
    emit ifcFilesDropped(paths);
}

// <# ************************************************************************************************>
bool ViewportPanel::acceptIfcDrop(QDropEvent* event) {
    const QStringList paths = modules::models::commands::ifcFilesFromMime(event->mimeData());
    if (paths.isEmpty()) return false;
    event->setDropAction(Qt::CopyAction);
    event->accept();
    return true;
}

// <# ************************************************************************************************>
bool ViewportPanel::eventFilter(QObject* watched, QEvent* event) {
#ifdef Q_OS_WIN
    if (watched == viewport_ && event->type() == QEvent::PlatformSurface) {
        auto* surface_event = static_cast<QPlatformSurfaceEvent*>(event);
        if (surface_event->surfaceEventType() == QPlatformSurfaceEvent::SurfaceAboutToBeDestroyed) {
            revokeNativeFileDrop();
        } else if (surface_event->surfaceEventType() == QPlatformSurfaceEvent::SurfaceCreated) {
            QMetaObject::invokeMethod(this, [this]() { registerNativeFileDrop(); }, Qt::QueuedConnection);
        }
    }
#endif

    const bool viewport_drag = watched == viewport_ || watched == viewport_container_;
#ifdef Q_OS_WIN
    // Explorer drops are delivered through the OLE target on the viewport HWND.
    // Handling the same drop as a Qt event as well would load the file twice.
    if (file_drop_target_ && viewport_drag) return QWidget::eventFilter(watched, event);
#endif
    if (viewport_drag && (event->type() == QEvent::DragEnter || event->type() == QEvent::DragMove)) {
        return acceptIfcDrop(static_cast<QDropEvent*>(event));
    }
    if (viewport_drag && event->type() == QEvent::Drop) {
        auto* drop = static_cast<QDropEvent*>(event);
        const QStringList paths = modules::models::commands::ifcFilesFromMime(drop->mimeData());
        if (paths.isEmpty()) return false;
        drop->setDropAction(Qt::CopyAction);
        drop->accept();
        deliverDroppedIfcFiles(paths);
        return true;
    }
    return QWidget::eventFilter(watched, event);
}

#ifdef Q_OS_WIN

// <# ************************************************************************************************>
void ViewportPanel::registerNativeFileDrop() {
    if (!viewport_) return;
    const auto hwnd = reinterpret_cast<HWND>(viewport_->winId());
    if (!hwnd || registered_drop_hwnd_ == hwnd) return;
    revokeNativeFileDrop();

    const HRESULT ole = OleInitialize(nullptr);
    if (FAILED(ole)) {
        qWarning() << "OleInitialize failed for viewport file drop" << ole;
        return;
    }
    ole_initialized_here_ = (ole == S_OK);

    auto* target = new FileDropTarget(this);
    const HRESULT registered = RegisterDragDrop(hwnd, target);
    if (FAILED(registered)) {
        qWarning() << "RegisterDragDrop failed for viewport file drop" << registered;
        target->Release();
        if (ole_initialized_here_) {
            OleUninitialize();
            ole_initialized_here_ = false;
        }
        return;
    }
    file_drop_target_ = target;
    registered_drop_hwnd_ = hwnd;
}

// <# ************************************************************************************************>
void ViewportPanel::revokeNativeFileDrop() {
    if (registered_drop_hwnd_) {
        RevokeDragDrop(reinterpret_cast<HWND>(registered_drop_hwnd_));
        registered_drop_hwnd_ = nullptr;
    }
    if (file_drop_target_) {
        static_cast<IDropTarget*>(file_drop_target_)->Release();
        file_drop_target_ = nullptr;
    }
    if (ole_initialized_here_) {
        OleUninitialize();
        ole_initialized_here_ = false;
    }
}

#endif

} // namespace bonsaiviewer::modules::viewport
