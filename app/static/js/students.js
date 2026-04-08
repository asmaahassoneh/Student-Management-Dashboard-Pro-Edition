document.addEventListener("DOMContentLoaded", () => {
  const pageData = document.getElementById("studentsPageData");
  const csrfToken = pageData?.dataset.csrfToken || "";

  const studentSearchInput = document.getElementById("studentSearchInput");
  const studentSearchForm = document.getElementById("studentSearchForm");
  const clearStudentSearchBtn = document.getElementById("clearStudentSearch");
  const studentsTableBody = document.getElementById("studentsTableBody");
  const studentsPagination = document.getElementById("studentsPagination");
  const studentMessage = document.getElementById("studentMessage");
  const studentLoading = document.getElementById("studentLoading");

  if (
    !studentSearchInput ||
    !studentSearchForm ||
    !clearStudentSearchBtn ||
    !studentsTableBody ||
    !studentsPagination ||
    !studentMessage ||
    !studentLoading
  ) {
    return;
  }

  function showStudentLoading(show) {
    studentLoading.classList.toggle("show", show);
  }

  function renderStudentRows(students) {
    if (!students.length) {
      studentsTableBody.innerHTML = `
        <tr>
          <td colspan="4" class="text-center text-muted">No students found.</td>
        </tr>
      `;
      return;
    }

    studentsTableBody.innerHTML = students
      .map(
        (student) => `
          <tr>
            <td>${student.name}</td>
            <td>${student.student_id}</td>
            <td>${student.courses_count}</td>
            <td>
              <a class="btn btn-sm btn-outline-primary" href="/students/${student.student_id}">View</a>
              <a class="btn btn-sm btn-primary" href="/students/${student.student_id}/edit">Edit</a>
              <form
                method="POST"
                action="/students/${student.student_id}/delete"
                class="d-inline"
                onsubmit="return confirm('Delete this student?');"
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

  function renderStudentPagination(page, pages) {
    if (pages <= 1) {
      studentsPagination.innerHTML = "";
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
    studentsPagination.innerHTML = html;

    studentsPagination.querySelectorAll("[data-page]").forEach((button) => {
      button.addEventListener("click", () => {
        loadStudents(Number(button.dataset.page));
      });
    });
  }

  async function loadStudents(page = 1) {
    const search = studentSearchInput.value.trim();

    showStudentLoading(true);
    studentMessage.innerHTML = "";

    try {
      const response = await fetch(
        `/api/students?search=${encodeURIComponent(search)}&page=${page}&per_page=5`
      );
      const data = await response.json();

      if (!response.ok || !data.success) {
        studentMessage.innerHTML = `
          <div class="alert alert-danger">Failed to load students.</div>
        `;
        return;
      }

      renderStudentRows(data.data || []);
      renderStudentPagination(data.page || 1, data.pages || 1);
    } catch (error) {
      studentMessage.innerHTML = `
        <div class="alert alert-danger">Something went wrong while loading students.</div>
      `;
    } finally {
      showStudentLoading(false);
    }
  }

  studentSearchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    loadStudents(1);
  });

  clearStudentSearchBtn.addEventListener("click", () => {
    studentSearchInput.value = "";
    loadStudents(1);
  });
});