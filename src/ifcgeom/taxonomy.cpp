#include "../ifcparse/IfcLogger.h"
#include "taxonomy.h"
#include "profile_helper.h"
#include "function_item_evaluator.h"

using namespace ifcopenshell::geometry::taxonomy;

namespace {
	bool compare(const trimmed_curve& a, const trimmed_curve& b);

	bool compare(const collection& a, const collection& b);

	bool compare(const loop& a, const loop& b);

	bool compare(const face& a, const face& b);

	bool compare(const shell& a, const shell& b);

	bool compare(const solid& a, const solid& b);

	bool compare(const loft& a, const loft& b);

	bool compare(const boolean_result& a, const boolean_result& b);

	template <typename T>
	bool compare(const eigen_base<T>& t, const eigen_base<T>& u) {
		if (t.components_ == nullptr && u.components_ == nullptr) {
			return false;
		}
		else if (t.components_ == nullptr && u.components_ != nullptr) {
			return true;
		}
		else if (t.components_ != nullptr && u.components_ == nullptr) {
			return false;
		}

		auto t_begin = t.components_->data();
		auto t_end = t.components_->data() + t.components_->size();

		auto u_begin = u.components_->data();
		auto u_end = u.components_->data() + u.components_->size();

		return std::lexicographical_compare(t_begin, t_end, u_begin, u_end);
	}

	bool compare(const line& a, const line& b) {
		return compare(*a.matrix, *b.matrix);
	}

	bool compare(const plane& a, const plane& b) {
		return compare(*a.matrix, *b.matrix);
	}

	bool compare(const circle& a, const circle& b) {
		if (a.radius == b.radius) {
			return compare(*a.matrix, *b.matrix);
		}
		return a.radius < b.radius;
	}

	bool compare(const ellipse& a, const ellipse& b) {
		if (a.radius == b.radius && a.radius2 == b.radius2) {
			return compare(*a.matrix, *b.matrix);
		}
		return
			std::tie(a.radius, a.radius2) <
			std::tie(b.radius, b.radius2);
	}

	bool compare(const bspline_curve&, const bspline_curve&) {
		throw std::runtime_error("not implemented");
	}

	template <typename T>
	typename std::enable_if<std::is_base_of<item, T>::value, int>::type less_to_order(const T& a, const T& b) {
		const bool a_lt_b = compare(a, b);
		const bool b_lt_a = compare(b, a);
		return a_lt_b ?
			-1 : (!b_lt_a ? 0 : 1);
	}

	template <typename T>
	typename std::enable_if<!std::is_base_of<item, T>::value, int>::type less_to_order(const T& a, const T& b) {
		const bool a_lt_b = a < b;
		const bool b_lt_a = b < a;
		return a_lt_b ?
			-1 : (!b_lt_a ? 0 : 1);
	}

	template <typename T>
	int less_to_order_optional(const boost::optional<T>& a, const boost::optional<T>& b) {
		if (a && b) {
			return less_to_order(*a, *b);
		}
		else if (!a && !b) {
			return 0;
		}
		else if (a) {
			return 1;
		}
		else {
			return -1;
		}
	}

	int compare(const boost::variant<boost::blank, point3::ptr, double>& a, const boost::variant<boost::blank, point3::ptr, double>& b) {
		bool a_lt_b, b_lt_a;
		if (a.which() == 0) {
			return 0;
		} else if (a.which() == 1) {
			a_lt_b = compare(*boost::get<point3::ptr>(a), *boost::get<point3::ptr>(b));
			b_lt_a = compare(*boost::get<point3::ptr>(b), *boost::get<point3::ptr>(a));
		} else {
			a_lt_b = std::less<double>()(boost::get<double>(a), boost::get<double>(b));
			b_lt_a = std::less<double>()(boost::get<double>(b), boost::get<double>(a));
		}
		return a_lt_b ?
			-1 : (!b_lt_a ? 0 : 1);
	}

	bool compare(const extrusion& a, const extrusion& b) {
		// @todo extrusions can also have non-identity matrices right? perhaps it's time
		//       for a dedicated transform node and not on the abstract geom_item.
		const int order[3] = {
			less_to_order(a.basis, b.basis),
			less_to_order(a.direction, b.direction),
			a.depth < b.depth ? -1 : (a.depth == b.depth ? 0 : 1)
		};
		auto it = std::find_if(std::begin(order), std::end(order), [](int x) { return x; });
		if (it == std::end(order)) return false;
		return *it == -1;
	}

	bool compare(const node&, const node&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const offset_curve&, const offset_curve&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const revolve&, const revolve&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const bspline_surface&, const bspline_surface&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const cylinder&, const cylinder&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const sphere&, const sphere&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const torus&, const torus&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const sweep_along_curve&, const sweep_along_curve&) {
		throw std::runtime_error("not implemented");
	}

    bool compare(const function_item&, const function_item&) {
        throw std::runtime_error("not implemented");
    }

    bool compare(const functor_item&, const functor_item&) {
        throw std::runtime_error("not implemented");
    }

	bool compare(const piecewise_function&, const piecewise_function&) {
		throw std::runtime_error("not implemented");
	}

   bool compare(const gradient_function&, const gradient_function&) {
        throw std::runtime_error("not implemented");
   }

   bool compare(const cant_function&, const cant_function&) {
       throw std::runtime_error("not implemented");
   }

   bool compare(const offset_function&, const offset_function&) {
       throw std::runtime_error("not implemented");
   }

	bool compare(const style& a, const style& b) {
		const int order[5] = {
			less_to_order(a.name, b.name),
			less_to_order(a.diffuse, b.diffuse),
			less_to_order(a.specular, b.specular),
			less_to_order(a.specularity, b.specularity),
			less_to_order(a.transparency, b.transparency)
		};
		auto it = std::find_if(std::begin(order), std::end(order), [](int x) { return x; });
		if (it == std::end(order)) return false;
		return *it == -1;
	}

	/* A compile-time for loop over the taxonomy kinds */
	template <size_t N>
	struct dispatch_comparison {
		static bool dispatch(const item* a, const item* b) {
			if (N == a->kind() && N == b->kind()) {
				auto A = static_cast<const type_by_kind::type<N>*>(a);
				auto B = static_cast<const type_by_kind::type<N>*>(b);
				return compare(*A, *B);
			}
			else {
				return dispatch_comparison<N + 1>::dispatch(a, b);
			}
		}
	};

	template <>
	struct dispatch_comparison<type_by_kind::max> {
		static bool dispatch(const item*, const item*) {
			return false;
		}
	};
}

bool ifcopenshell::geometry::taxonomy::less(item::const_ptr a, item::const_ptr b) {
	if (a == b) {
		return false;
	}

	int a_kind = a->kind();
	int b_kind = b->kind();

	if (a_kind != b_kind) {
		return a_kind < b_kind;
	}

#ifdef TAXONOMY_USE_SHARED_PTR
	return dispatch_comparison<0>::dispatch(a.get(), b.get());
#endif
}


namespace {
	bool compare(const trimmed_curve& a, const trimmed_curve& b) {
		int a_which_start = a.start.which();
		int a_which_end = a.end.which();
		int b_which_start = b.start.which();
		int b_which_end = b.end.which();
		if (std::tie(a.orientation, a_which_start, a_which_end) ==
			std::tie(b.orientation, b_which_start, b_which_end)) {

			int start_state = compare(a.start, b.start);

			if (start_state == 0) {

				int end_state = compare(a.end, b.end);

				if (end_state == 0) {

					int a_has_basis = !!a.basis;
					int b_has_basis = !!a.basis;

					if (a_has_basis == b_has_basis) {

						if (!a_has_basis) {
							// Finally, equality
							return false;
						}
						else {
							return less(a.basis, b.basis);
						}

					}
					else {
						return a_has_basis < b_has_basis;
					}

				}
				else {
					return end_state == -1;
				}

			}
			else {
				return start_state == -1;
			}

		}
		else {
			return
				std::tie(a.orientation, a_which_start, a_which_end) <
				std::tie(b.orientation, b_which_start, b_which_end);
		}
	}

	template <typename T>
	bool compare_collection(const collection_base<T>& a, const collection_base<T>& b) {
		if (a.children.size() == b.children.size()) {
			auto at = a.children.begin();
			auto bt = b.children.begin();
			for (; at != a.children.end(); ++at, ++bt) {
				const bool a_lt_b = less(*at, *bt);
				const bool b_lt_a = less(*bt, *at);
				if (!a_lt_b && !b_lt_a) {
					// Elements equal.
					continue;
				}
				return a_lt_b;
			}
			// Vectors equal, compare matrix (in case of mapped items).
			return compare(*a.matrix, *b.matrix);
		}
		else {
			return a.children.size() < b.children.size();
		}
	}

	bool compare(const loop& a, const loop& b) {
		return compare_collection<edge>(a, b);
	}

	bool compare(const face& a, const face& b) {
		return compare_collection<loop>(a, b);
	}

	bool compare(const shell& a, const shell& b) {
		return compare_collection<face>(a, b);
	}

	bool compare(const solid& a, const solid& b) {
		return compare_collection<shell>(a, b);
	}

	bool compare(const loft& a, const loft& b) {
		return compare_collection<geom_item>(a, b);
	}

	bool compare(const collection& a, const collection& b) {
		return compare_collection<geom_item>(a, b);
	}

	bool compare(const boolean_result& a, const boolean_result& b) {
		return compare_collection<geom_item>(a, b);
	}
}

ifcopenshell::geometry::taxonomy::solid::ptr ifcopenshell::geometry::create_box(double dx, double dy, double dz) {
	return create_box(0., 0., 0., dx, dy, dz);
}

ifcopenshell::geometry::taxonomy::solid::ptr ifcopenshell::geometry::create_box(double x, double y, double z, double dx, double dy, double dz) {
	auto solid = make<taxonomy::solid>();
	auto shell = make<taxonomy::shell>();
	solid->children.push_back(shell);

	// x = 0
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0, y + 0,  z + 0),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + 0),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + 0, y + 0,  z + dz)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// x = dx
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + dx, y + 0,  z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0,  z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + 0)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// y = 0
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0,  y + 0, z + 0),
			taxonomy::make<taxonomy::point3>(x + 0,  y + 0, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0, z + 0)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// y = dy
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + dz)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// z = 0
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0, y + 0, z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0, z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + 0),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + 0)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// z = dz
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0, y + 0, z + dz),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0, z + dz)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	return solid;
}

///////////////////
piecewise_function::piecewise_function(double start, const spans_t& s, const IfcUtil::IfcBaseInterface* instance) : function_item(instance), start_(start), spans_(s) {
}

piecewise_function::piecewise_function(double start, const std::vector<piecewise_function::ptr>& pwfs, const IfcUtil::IfcBaseInterface* instance) : function_item(instance), start_(start) {
    for (auto& pwf : pwfs) {
        spans_.insert(spans_.end(), pwf->spans().begin(), pwf->spans().end());
    }
};

const piecewise_function::spans_t& piecewise_function::spans() const { return spans_; }
bool piecewise_function::is_empty() const { return spans_.empty(); }
double piecewise_function::start() const { return start_; }
double piecewise_function::end() const { return start_ + length(); }
double piecewise_function::length() const {
    return std::accumulate(spans_.begin(), spans_.end(), 0.0, [](const auto& v, const auto& s) { return v + s->length(); });

    // this is a secondary option where we only compute length once and cache it.
    // mutex is needed to prevent interruption of the accumulation if there is multi-threading
    // skipping this detail for now and just adding up the span lengths every time
    //if (!length_.has_value()) {
    //    length_ = std::accumulate(spans_.begin(), spans_.end(), 0.0, [](const auto& v, const auto& s) { return v + s->length(); });
    //}
    //return *length_;
}


gradient_function::gradient_function(piecewise_function::const_ptr horizontal, piecewise_function::const_ptr vertical, const IfcUtil::IfcBaseInterface* instance) : 
	function_item(instance), horizontal_(horizontal), vertical_(vertical) {
}
double gradient_function::start() const { return std::max(horizontal_->start(), vertical_->start()); }
double gradient_function::end() const { return std::min(horizontal_->end(), vertical_->end()); }
piecewise_function::const_ptr gradient_function::get_horizontal() const { return horizontal_; }
piecewise_function::const_ptr gradient_function::get_vertical() const { return vertical_; }


cant_function::cant_function(gradient_function::const_ptr gradient, piecewise_function::const_ptr cant, const IfcUtil::IfcBaseInterface* instance) : 
	function_item(instance), gradient_(gradient), cant_(cant) {
}
double cant_function::start() const { return std::max(gradient_->start(), cant_->start()); }
double cant_function::end() const { return std::min(gradient_->end(), cant_->end()); }
gradient_function::const_ptr cant_function::get_gradient() const { return gradient_; }
piecewise_function::const_ptr cant_function::get_cant() const { return cant_; }


offset_function::offset_function(function_item::const_ptr basis, piecewise_function::const_ptr offset, const IfcUtil::IfcBaseInterface* instance) : function_item(instance),
                                                                                                                                                                       basis_(basis),
                                                                                                                                                                       offset_(offset) {
}
double offset_function::start() const { return basis_->start(); }
double offset_function::end() const { return basis_->end(); }
function_item::const_ptr offset_function::get_basis() const { return basis_; }
piecewise_function::const_ptr offset_function::get_offset() const { return offset_; }


ifcopenshell::geometry::taxonomy::collection::ptr ifcopenshell::geometry::flatten(const taxonomy::collection::ptr& deep) {
	auto flat = make<taxonomy::collection>();
	ifcopenshell::geometry::visit<taxonomy::collection>(deep, [&flat](taxonomy::ptr i) {
		flat->children.push_back(taxonomy::cast<taxonomy::geom_item>(clone(i)));
		});
	return flat;
}

const std::string& ifcopenshell::geometry::taxonomy::kind_to_string(kinds k) {
	using namespace std::string_literals;

	static std::string values[] = {
        "matrix4"s,
        "point3"s,
        "direction3"s,
        "line"s,
        "circle"s,
        "ellipse"s,
        "bspline_curve"s,
        "offset_curve"s,
        "plane"s,
        "cylinder"s,
        "sphere"s,
        "torus"s,
        "bspline_surface"s,
        "edge"s,
        "loop"s,
        "face"s,
        "shell"s,
        "solid"s,
        "loft"s,
        "extrusion"s,
        "revolve"s,
        "sweep_along_curve"s,
        "node"s,
        "collection"s,
        "boolean_result"s,
        "function_item"s,
        "functor_item"s,
        "piecewise_function"s,
        "gradient_function"s,
        "cant_function"s,
        "offset_function"s,
        "colour"s,
        "style"s,
	};

	return values[k];
}

std::atomic_uint32_t item::counter_(0);

void ifcopenshell::geometry::taxonomy::item::print(std::ostream& o, int indent) const {
	o << std::string(indent, ' ') << kind_to_string(kind()) << std::endl;
}

void ifcopenshell::geometry::taxonomy::matrix4::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geometry::taxonomy::colour::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geometry::taxonomy::style::print(std::ostream& o, int indent) const {
	o << std::string(indent, ' ') << "style" << std::endl;
	o << std::string(indent, ' ') << "     " << "name " << (name) << std::endl;
	if (diffuse.components_) {
		o << std::string(indent, ' ') << "     " << "diffuse" << std::endl;
		diffuse.print(o, indent + 5 + 7);
	}
	if (specular.components_) {
		o << std::string(indent, ' ') << "     " << "specular" << std::endl;
		specular.print(o, indent + 5 + 8);
	}
	// @todo
}

void ifcopenshell::geometry::taxonomy::point3::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geometry::taxonomy::direction3::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geometry::taxonomy::line::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geometry::taxonomy::circle::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
	o << std::string(indent + 4, ' ') << "radius " << radius << std::endl;
}

void ifcopenshell::geometry::taxonomy::ellipse::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
	o << std::string(indent + 4, ' ') << "radii " << radius << " " << radius2 << std::endl;
}

void ifcopenshell::geometry::taxonomy::trimmed_curve::print(std::ostream& o, int indent) const {
	o << std::string(indent, ' ') << kind_to_string(kind());
	if (!this->orientation.get_value_or(true)) {
		o << " [R]";
	} else {
		o << " [ ]";
	}
	if (!this->curve_sense.get_value_or(true)) {
		o << " [R]";
	} else {
		o << " [ ]";
	}
	o << std::endl;
	if (basis) {
		basis->print(o, indent + 4);
	}

	const boost::variant<boost::blank, point3::ptr, double>* const start_end[2] = { &start, &end };
	for (int i = 0; i < 2; ++i) {
		o << std::string(indent + 4, ' ') << (i == 0 ? "start" : "end") << std::endl;
		if (start_end[i]->which() == 1) {
			boost::get<point3::ptr>(*start_end[i])->print(o, indent + 4);
		} else if (start_end[i]->which() == 2) {
			o << std::string(indent + 4, ' ') << "parameter " << boost::get<double>(*start_end[i]) << std::endl;
		}
	}

	if (this->instance) {
		std::ostringstream oss;
		this->instance->as<IfcUtil::IfcBaseClass>()->toString(oss);
		o << std::string(indent + 4, ' ') << oss.str() << std::endl;
	}
}

void ifcopenshell::geometry::taxonomy::extrusion::print(std::ostream& o, int indent) const {
	o << std::string(indent, ' ') << "extrusion " << depth << std::endl;
	direction->print(o, indent + 4);
	basis->print(o, indent + 4);
}

boost::optional<face::ptr> ifcopenshell::geometry::taxonomy::loop_to_face_upgrade_impl(ptr item) {
	boost::optional<face::ptr> face_;
	auto loop_ = dcast<loop>(item);
		if (loop_) {
			loop_->external = true;

			face_ = make<face>();
			(*face_)->instance = loop_->instance;
			(*face_)->matrix = loop_->matrix;
			(*face_)->children = { clone(loop_) };
		}
	return face_;
}

boost::optional<edge::ptr> ifcopenshell::geometry::taxonomy::curve_to_edge_upgrade_impl(ptr item) {
	boost::optional<edge::ptr> edge_;
	auto circle_ = dcast<circle>(item);
	auto ellipse_ = dcast<ellipse>(item);
	auto line_ = dcast<line>(item);
	auto bspline_curve_ = dcast<bspline_curve>(item);
	if (circle_ || ellipse_ || line_ || bspline_curve_) {
		edge_ = make<edge>();
		if (circle_) {
			(*edge_)->basis = circle_;
			(*edge_)->instance = circle_->instance;
		} else if (ellipse_) {
			(*edge_)->basis = ellipse_;
			(*edge_)->instance = ellipse_->instance;
		} else if (line_) {
			(*edge_)->basis = line_;
			(*edge_)->instance = line_->instance;
		} else if (bspline_curve_) {
			(*edge_)->basis = bspline_curve_;
			(*edge_)->instance = bspline_curve_->instance;
		}

		if (circle_ || ellipse_) {
			// @todo
			(*edge_)->start = 0.;
			(*edge_)->end = 2 * boost::math::constants::pi<double>();
		}
	}
	return edge_;
}

boost::optional<loop::ptr> ifcopenshell::geometry::taxonomy::curve_to_loop_upgrade_impl(ptr item) {
	boost::optional<loop::ptr> loop_;
	auto circle_ = dcast<circle>(item);
	auto ellipse_ = dcast<ellipse>(item);
	auto line_ = dcast<line>(item);
	auto bspline_curve_ = dcast<bspline_curve>(item);
	if (circle_ || ellipse_ || line_ || bspline_curve_) {
		auto edge_ = make<edge>();
		if (circle_) {
			edge_->basis = circle_;
		} else if (ellipse_) {
			edge_->basis = ellipse_;
		} else if (line_) {
			edge_->basis = line_;
		} else if (bspline_curve_) {
			edge_->basis = bspline_curve_;
		}

		if (circle_ || ellipse_) {
			// @todo
			edge_->start = 0.;
			edge_->end = 2 * boost::math::constants::pi<double>();
		}

		loop_ = make<loop>();
		(*loop_)->children.push_back(edge_);
	}
	return loop_;
}

boost::optional<loop::ptr> ifcopenshell::geometry::taxonomy::edge_to_loop_upgrade_impl(ptr item) {
	boost::optional<loop::ptr> loop_;
	auto edge_ = dcast<edge>(item);
	if (edge_) {
		loop_ = make<loop>();
		(*loop_)->children.push_back(edge_);
	}
	return loop_;
}

boost::optional<face::ptr> ifcopenshell::geometry::taxonomy::curve_to_face_upgrade_impl(ptr item) {
    boost::optional<face::ptr> face_;
    auto circle_ = dcast<circle>(item);
    auto ellipse_ = dcast<ellipse>(item);
    auto line_ = dcast<line>(item);
    auto bspline_curve_ = dcast<bspline_curve>(item);

    if (circle_ || ellipse_ || line_ || bspline_curve_) {
        auto edge_ = make<edge>();
        if (circle_) {
            edge_->basis = circle_;
        } else if (ellipse_) {
            edge_->basis = ellipse_;
        } else if (line_) {
            edge_->basis = line_;
        } else if (bspline_curve_) {
            edge_->basis = bspline_curve_;
        }

        if (circle_ || ellipse_) {
            // @todo
            edge_->start = 0.;
            edge_->end = 2 * boost::math::constants::pi<double>();
        }

        auto loop_ = make<loop>();
        loop_->children.push_back(edge_);

        face_ = make<face>();
        (*face_)->instance = loop_->instance;
        (*face_)->matrix = loop_->matrix;
        (*face_)->children = { clone(loop_) };
    }
    return face_;
}

namespace {
	// @todo eliminate redundancy with cgal kernel
	void evaluate_curve(const circle::ptr& c, double u, point3& p) {
		Eigen::Vector4d xy{ c->radius * std::cos(u), c->radius * std::sin(u), 0, 1. };
		p.components() = (c->matrix->ccomponents() * xy).head<3>();
	}

	// @todo eliminate redundancy with cgal kernel
	void evaluate_curve_d1(const circle::ptr& c, double u, direction3& p) {
		Eigen::Vector4d xy{ -std::sin(u), cos(u), 0, 0. };
		p.components() = (c->matrix->ccomponents() * xy).head<3>();
	}

	double project_onto_curve(const circle::ptr& c, const point3& p) {
		Eigen::Vector2d xy = (c->matrix->ccomponents().inverse() * p.ccomponents().homogeneous()).head<2>();
		return std::atan2(xy(1), xy(0));
	}
}


boost::optional<function_item::ptr> ifcopenshell::geometry::taxonomy::loop_to_function_item_upgrade_impl(ptr item) {
	boost::optional<function_item::ptr> fi_;
	auto loop_ = dcast<loop>(item);
	if (loop_) {
		if (loop_->fi.is_initialized()) {
			fi_ = loop_->fi;
		} else {
         // piecewise_function is a specialization of function_item - callers don't need to know this detail
			piecewise_function::spans_t spans;
			spans.reserve(loop_->children.size());
			for (auto& edge_ : loop_->children) {
				if (edge_->basis && edge_->basis->kind() == CIRCLE) {
					const circle::ptr circ = std::static_pointer_cast<circle>(edge_->basis);

					auto* s_pnt = boost::get<point3::ptr>(&edge_->start);
					auto* e_pnt = boost::get<point3::ptr>(&edge_->end);
					auto* s_param = boost::get<double>(&edge_->start);
					auto* e_param = boost::get<double>(&edge_->end);

					if (!s_pnt && !s_param) {
						return boost::none;
					}
					if (!e_pnt && !e_param) {
						return boost::none;
					}

					double s = s_pnt ? project_onto_curve(circ, **s_pnt) : *s_param;
					double e = e_pnt ? project_onto_curve(circ, **e_pnt) : *e_param;

					auto l = std::fabs(s - e) * circ->radius;
					std::function<Eigen::Matrix4d(double)> fn = [circ, s](double u) {
						point3 P;
						direction3 d;
						evaluate_curve(circ, u / circ->radius + s, P);
						evaluate_curve_d1(circ, u / circ->radius + s, d);
						return matrix4(P.ccomponents(), circ->matrix->ccomponents().col(2).head<3>(), d.ccomponents()).components();
					};
					spans.emplace_back(taxonomy::make<taxonomy::functor_item>(l, fn));
				} else if (edge_->start.which() == 1 && edge_->end.which() == 1) {
					if (edge_->basis && edge_->basis->kind() != LINE) {
						Logger::Message(Logger::Severity::LOG_WARNING, "Basis curve not supported - edge is treated as a straight line edge");
					}
					const auto& s = boost::get<point3::ptr>(edge_->start)->ccomponents();
					const auto& e = boost::get<point3::ptr>(edge_->end)->ccomponents();
					Eigen::Vector3d v = e - s;
					auto l = v.norm(); // the norm of a vector is a measure of its length
					v.normalize();     // normalize the vector so that it is a unit direction vector
					std::function<Eigen::Matrix4d(double)> fn = [s, v](double u) {
						Eigen::Vector3d o(s + u * v), axis(0, 0, 1), refDirection(v);
						auto Y = axis.cross(refDirection).normalized();
						axis = refDirection.cross(Y).normalized();
						return make<matrix4>(o, axis, refDirection)->components();
					};
					spans.emplace_back(taxonomy::make<taxonomy::functor_item>(l, fn));
				} else {
					Logger::Message(Logger::Severity::LOG_ERROR, "Basis curve not supported");
					return boost::none;
				}
			}
			fi_ = make<piecewise_function>(0.0,spans);
			loop_->fi = fi_;
		}
	}
    return fi_;
}
