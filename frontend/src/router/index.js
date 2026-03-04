import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../store/auth.js";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("../pages/LoginPage.vue"),
    meta: { guest: true },
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("../pages/RegisterPage.vue"),
    meta: { guest: true },
  },
  {
    path: "/verify",
    name: "VerifyEmail",
    component: () => import("../pages/VerifyEmailPage.vue"),
  },
  {
    path: "/",
    name: "Dashboard",
    component: () => import("../pages/DashboardPage.vue"),
    meta: { auth: true },
  },
  {
    path: "/products/:id",
    name: "ProductDetail",
    component: () => import("../pages/ProductDetailPage.vue"),
    meta: { auth: true },
    props: true,
  },
  {
    path: "/admin",
    name: "Admin",
    component: () => import("../pages/AdminPage.vue"),
    meta: { auth: true, admin: true },
  },
  {
    path: "/settings",
    name: "Settings",
    component: () => import("../pages/SettingsPage.vue"),
    meta: { auth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore();

  if (to.meta.auth && !auth.isLoggedIn) {
    return next({ name: "Login" });
  }
  if (to.meta.admin && auth.user && !auth.user.is_admin) {
    return next({ name: "Dashboard" });
  }
  if (to.meta.guest && auth.isLoggedIn) {
    return next({ name: "Dashboard" });
  }
  next();
});

export default router;
