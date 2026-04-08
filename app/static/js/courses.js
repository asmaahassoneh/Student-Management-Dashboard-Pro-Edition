document.addEventListener("DOMContentLoaded", () => {
  const config = window.coursesPageConfig || {};
  const courseSearchInput = document.getElementById("courseSearchInput");
  const courseSearchForm = document.getElementById("courseSearchForm");
  const clearCourseSearchBtn = document.getElementById("clearCourseSearch");
  const coursesTableBody = document.getElementById("coursesTableBody");
  const coursesPagination = document.getElementById("coursesPagination");
  const courseMessage = document.getElementById("courseMessage");
  const courseLoading = document.getElementById("courseLoading");

  if (
    !courseSearchInput ||
    !courseSearchForm ||
    !clearCourseSearchBtn ||
    !coursesTableBody ||
    !coursesPagination ||
    !courseMessage ||
    !courseLoading
  ) {
    return;
  }

  const csrfToken = config.csrfToken || "";

  function showCourseLoading(show) {
    courseLoading.classList.toggle("show", show);
  }

  function renderCourseRows(courses) {
    if (!courses.length) {
      coursesTableBody.innerHTML = `
        <tr>
          <td colspan="5" class="text-center text-muted">No courses found.</td>
        </tr>
      `;
      return;
    }

    coursesTableBody.innerHTML = courses
      .map(
        (course) => `
          <tr>
            <td>${course.name}</td>
            <td>${course.code}</td>
            <td>${course.description || "-"}</td>
            <td>${course.students_count}</td>
            <td>
              <a class="btn btn-sm btn-primary" href="/courses/${course.id}/edit">Edit</a>
              <form
                method="POST"
                action="/courses/${course.id}/delete"
                class="d-inline"
                onsubmit="return confirm('Delete this course?');"
              >
                <input type="hidden" name="csrf_token" value="${csrfToken}">
                <button type="submit" class="btn btn-sm btn-danger">Delete</button>
              </form>
            </td>
          </tr>
        `
      )
      .join("");
  }

  function renderCoursePagination(page, pages) {
    if (pages <= 1) {
      coursesPagination.innerHTML = "";
      return;
    }

    let html = `<nav><ul class="pagination">`;

    html += `
      <li class="page-item ${page <= 1 ? "disabled" : ""}">
        <button class="page-link" data-page="${page - 1}" ${page <= 1 ? "disabled" : ""}>Previous</button>
      </li>
    `;

    for (let i = 1; i <= pages; i += 1) {
      html += `
        <li class="page-item ${i === page ? "active" : ""}">
          <button class="page-link" data-page="${i}">${i}</button>
        </li>
      `;
    }

    html += `
      <li class="page-item ${page >= pages ? "disabled" : ""}">
        <button class="page-link" data-page="${page + 1}" ${page >= pages ? "disabled" : ""}>Next</button>
      </li>
    `;

    html += `</ul></nav>`;
    coursesPagination.innerHTML = html;

    coursesPagination.querySelectorAll("[data-page]").forEach((button) => {
      button.addEventListener("click", () => {
        loadCourses(Number(button.dataset.page));
      });
    });
  }

  async function loadCourses(page = 1) {
    const search = courseSearchInput.value.trim();

    showCourseLoading(true);
    courseMessage.innerHTML = "";

    try {
      const response = await fetch(
        `/api/courses?search=${encodeURIComponent(search)}&page=${page}&per_page=5`
      );
      const data = await response.json();

      if (!response.ok || !data.success) {
        courseMessage.innerHTML = `
          <div class="alert alert-danger">Failed to load courses.</div>
        `;
        return;
      }

      renderCourseRows(data.data || []);
      renderCoursePagination(data.page || 1, data.pages || 1);
    } catch (error) {
      courseMessage.innerHTML = `
        <div class="alert alert-danger">Something went wrong while loading courses.</div>
      `;
    } finally {
      showCourseLoading(false);
    }
  }

  courseSearchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    loadCourses(1);
  });

  clearCourseSearchBtn.addEventListener("click", () => {
    courseSearchInput.value = "";
    loadCourses(1);
  });
});