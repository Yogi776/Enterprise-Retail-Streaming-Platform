"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  LayoutDashboard,
  ShoppingCart,
  CreditCard,
  Package,
  Truck,
  AlertTriangle,
  Users,
  BarChart3,
  TrendingUp,
  Target,
  Database,
  GitBranch,
  CheckCircle,
  BarChart,
  Bot,
  Bell,
  FileText,
  Settings,
  ChevronDown,
  ChevronRight,
  Sparkles,
} from "lucide-react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  badge?: number;
  roles?: string[];
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const NAV_STRUCTURE: NavGroup[] = [
  {
    label: "EXECUTIVE",
    items: [
      { label: "Overview", href: "/executive", icon: LayoutDashboard },
    ],
  },
  {
    label: "LIVE OPERATIONS",
    items: [
      { label: "Orders", href: "/live-operations/orders", icon: ShoppingCart },
      { label: "Payments", href: "/live-operations/payments", icon: CreditCard },
      { label: "Inventory", href: "/live-operations/inventory", icon: Package },
      { label: "Delivery", href: "/live-operations/delivery", icon: Truck },
      { label: "Fraud", href: "/live-operations/fraud", icon: AlertTriangle },
    ],
  },
  {
    label: "CUSTOMER INTELLIGENCE",
    items: [
      { label: "Customer 360", href: "/customer-intelligence/customer-360", icon: Users },
      { label: "Segments", href: "/customer-intelligence/segments", icon: BarChart3 },
      { label: "Behavior", href: "/customer-intelligence/behavior", icon: TrendingUp },
    ],
  },
  {
    label: "PRODUCT INTELLIGENCE",
    items: [
      { label: "Performance", href: "/product-intelligence/performance", icon: BarChart },
      { label: "Category", href: "/product-intelligence/category", icon: Target },
      { label: "Recommendations", href: "/product-intelligence/recommendations", icon: Sparkles },
    ],
  },
  {
    label: "DATA PRODUCTS",
    items: [
      { label: "Catalog", href: "/data-products/catalog", icon: Database },
      { label: "Lineage", href: "/data-products/lineage", icon: GitBranch },
      { label: "Quality", href: "/data-products/quality", icon: CheckCircle },
      { label: "Usage", href: "/data-products/usage", icon: BarChart },
    ],
  },
];

const FOOTER_ITEMS: NavItem[] = [
  { label: "AI Assistant", href: "/ai-assistant", icon: Bot },
  { label: "Alerts", href: "/alerts", icon: Bell, badge: 3 },
  { label: "Reports", href: "/reports", icon: FileText },
  { label: "Admin", href: "/admin", icon: Settings, roles: ["DATA_PLATFORM_ENGINEER"] },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(
    new Set(["EXECUTIVE", "LIVE OPERATIONS", "CUSTOMER INTELLIGENCE", "PRODUCT INTELLIGENCE", "DATA PRODUCTS"])
  );
  const pathname = usePathname();

  const toggleGroup = (label: string) => {
    setExpandedGroups((prev) => {
      const next = new Set(prev);
      if (next.has(label)) {
        next.delete(label);
      } else {
        next.add(label);
      }
      return next;
    });
  };

  return (
    <aside
      className={`
        flex flex-col h-full bg-slate-900 text-slate-100 transition-all duration-200
        ${collapsed ? "w-16" : "w-60"}
      `}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-slate-800">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
          <TrendingUp className="w-5 h-5 text-white" />
        </div>
        {!collapsed && (
          <div className="flex flex-col min-w-0">
            <span className="font-semibold text-sm truncate">Retail</span>
            <span className="text-xs text-slate-400 truncate">Command Center</span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 scrollbar-thin scrollbar-thumb-slate-700">
        {NAV_STRUCTURE.map((group) => (
          <div key={group.label} className="mb-2">
            {/* Group Header */}
            <button
              onClick={() => toggleGroup(group.label)}
              className="flex items-center gap-2 w-full px-4 py-1.5 text-xs font-medium text-slate-500 uppercase tracking-wider hover:text-slate-300 transition-colors"
            >
              {!collapsed && (
                <>
                  <span className="flex-1 text-left">{group.label}</span>
                  {expandedGroups.has(group.label) ? (
                    <ChevronDown className="w-3 h-3" />
                  ) : (
                    <ChevronRight className="w-3 h-3" />
                  )}
                </>
              )}
              {collapsed && <ChevronRight className="w-3 h-3 mx-auto" />}
            </button>

            {/* Group Items */}
            {expandedGroups.has(group.label) && (
              <div className="space-y-0.5 px-2">
                {group.items.map((item) => {
                  const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                  const Icon = item.icon;

                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`
                        flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors relative
                        ${isActive
                          ? "bg-blue-600/20 text-blue-400 border-l-2 border-blue-500"
                          : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                        }
                      `}
                      title={collapsed ? item.label : undefined}
                    >
                      <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? "text-blue-400" : ""}`} />
                      {!collapsed && (
                        <span className="flex-1 truncate">{item.label}</span>
                      )}
                      {!collapsed && item.badge && item.badge > 0 && (
                        <span className="flex-shrink-0 bg-red-500 text-white text-xs font-medium px-1.5 py-0.5 rounded-full">
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </nav>

      {/* Footer Items */}
      <div className="border-t border-slate-800 py-4 px-2 space-y-0.5">
        {FOOTER_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors
                ${isActive
                  ? "bg-blue-600/20 text-blue-400 border-l-2 border-blue-500"
                  : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                }
              `}
              title={collapsed ? item.label : undefined}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {!collapsed && (
                <>
                  <span className="flex-1">{item.label}</span>
                  {item.badge && item.badge > 0 && (
                    <span className="flex-shrink-0 bg-red-500 text-white text-xs font-medium px-1.5 py-0.5 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </Link>
          );
        })}

        {/* Collapse Toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-slate-500 hover:bg-slate-800 hover:text-slate-300 transition-colors w-full mt-2"
        >
          <ChevronRight className={`w-4 h-4 flex-shrink-0 transition-transform ${collapsed ? "" : "rotate-180"}`} />
          {!collapsed && <span className="flex-1">Collapse</span>}
        </button>
      </div>
    </aside>
  );
}