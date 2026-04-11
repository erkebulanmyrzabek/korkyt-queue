import { createRouter, createWebHistory } from "vue-router";

import { getInstructorToken } from "../api";
import AdminDashboard from "../views/admin/AdminDashboard.vue";
import InstructorLogin from "../views/instructor/InstructorLogin.vue";
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
      meta: {
        titleKey: "platform.adminTitle",
        subtitleKey: "platform.adminSubtitle",
      },
    },
    {
      path: "/instructor",
      name: "instructor",
      component: InstructorDashboard,
      meta: {
        requiresInstructorAuth: true,
        titleKey: "platform.instructorTitle",
        subtitleKey: "platform.instructorSubtitle",
      },
    },
    {
      path: "/instructor/login",
      name: "instructor-login",
      component: InstructorLogin,
      meta: {
        titleKey: "platform.instructorTitle",
        subtitleKey: "platform.instructorSubtitle",
      },
    },
    {
      path: "/tv",
      name: "tv",
      component: TvDisplay,
    },
  ],
});

router.beforeEach((to) => {
  const token = getInstructorToken();

  if (to.meta.requiresInstructorAuth && !token) {
    return { name: "instructor-login" };
  }

  if (to.name === "instructor-login" && token) {
    return { name: "instructor" };
  }

  return true;
});
