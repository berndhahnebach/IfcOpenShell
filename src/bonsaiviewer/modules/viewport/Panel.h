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

#ifndef IFCINTERFACE_MODULES_VIEWPORT_PANEL_H
#define IFCINTERFACE_MODULES_VIEWPORT_PANEL_H

#include <QStringList>
#include <QWidget>

class QDropEvent;
class ViewportWindow;

namespace bonsaiviewer::modules::viewport {

class ViewportPanel : public QWidget {
    Q_OBJECT

public:
    explicit ViewportPanel(QWidget* parent = nullptr);
    ~ViewportPanel() override;

    ViewportWindow* viewport() const { return viewport_; }
    void deliverDroppedIfcFiles(const QStringList& paths);

signals:
    void ifcFilesDropped(const QStringList& paths);

protected:
    bool eventFilter(QObject* watched, QEvent* event) override;

private:
    bool acceptIfcDrop(QDropEvent* event);

#ifdef Q_OS_WIN
    void registerNativeFileDrop();
    void revokeNativeFileDrop();
    void* file_drop_target_ = nullptr;
    void* registered_drop_hwnd_ = nullptr;
    bool ole_initialized_here_ = false;
#endif

    ViewportWindow* viewport_ = nullptr;
    QWidget* viewport_container_ = nullptr;
};

} // namespace bonsaiviewer::modules::viewport

#endif
