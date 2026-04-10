import { createRouter, createWebHistory } from "vue-router";

import AdminDashboard from "../views/admin/AdminDashboard.vue";
import InstructorDashboard from "../views/instructor/InstructorDashboard.vue";
import TvDisplay from "../views/tv/TvDisplay.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      redirect: "/admin",
    },
    {
      path: "/admin",
      name: "admin",
      component: AdminDashboard,
    },
    {
      path: "/instructor",
      name: "instructor",
      component: InstructorDashboard,
    },
    {
      path: "/tv",
      name: "tv",
      component: TvDisplay,
    },
  ],
});

