document.addEventListener("DOMContentLoaded", () => {
  const pageData = document.getElementById("usersPageData");
  const csrfToken = pageData?.dataset.csrfToken || "";
  const currentUserId = Number(pageData?.dataset.currentUserId || 0);

  const userSearchForm = document.getElementById("userSearchForm");
  const userSearchInput = document.getElementById("userSearchInput");
  const clearUserSearchBtn = document.getElementById("clearUserSearch");
  const usersTableBody = document.getElementById("usersTableBody");
  const usersPagination = document.getElementById("usersPagination");
  const userLoading = document.getElementById("userLoading");

  if (
    !userSearchForm ||
    !userSearchInput ||
    !clearUserSearchBtn ||
    !usersTableBody ||
    !usersPagination ||
    !userLoading
  ) {
    return;
  }

  function toggleUserLoading(show) {
    userLoading.classList.toggle("show", show);
  }

  function renderUserRows(users) {
    if (!users.length) {
      usersTableBody.innerHTML = `
        <tr>
          <td colspan="5" class="table-empty">No users found.</td>
        </tr>
      `;
      return;
    }

    usersTableBody.innerHTML = users
      .map(
        (user) => `
          <tr>
            <td>
              ${
                user.profile_picture
                  ? `<img src="/static/uploads/${user.profile_picture}" alt="Profile" class="table-profile-pic" />`
                  : "-"
              }
            </td>
            <td>${user.username}</td>
            <td>${user.email}</td>
            <td>
              <span class="role-badge">
                ${user.role.charAt(0).toUpperCase() + user.role.slice(1)}
              </span>
            </td>
            <td>
              <div class="table-actions">
                <a class="btn secondary-btn" href="/users/${user.id}">View</a>
                <a class="btn" href="/users/${user.id}/edit">Edit</a>
                ${
                  user.id !== currentUserId
                    ? `
                      <form method="POST" action="/users/${user.id}/delete" onsubmit="return confirm('Delete this user?');">
                        <input type="hidden" name="csrf_token" value="${csrfToken}">
                        <button type="submit" class="btnDelete danger-btn">Delete</button>
                      </form>
                    `
                    : ""
                }
              </div>
            </td>
          </tr>
        `
      )
      .join("");
  }

  function renderUserPagination(page, pages) {
    if (pages <= 1) {
      usersPagination.innerHTML = "";
      return;
    }

    let html = `<div class="pagination-ui">`;

    html += `
      <button
        type="button"
        class="btn secondary-btn"
        data-page="${page - 1}"
        ${page <= 1 ? "disabled" : ""}
      >
        Previous
      </button>
    `;

    for (let i = 1; i <= pages; i += 1) {
      html += `
        <button
          type="button"
          class="btn secondary-btn page-number ${i === page ? "active" : ""}"
          data-page="${i}"
        >
          ${i}
        </button>
      `;
    }

    html += `
      <button
        type="button"
        class="btn secondary-btn"
        data-page="${page + 1}"
        ${page >= pages ? "disabled" : ""}
      >
        Next
      </button>
    `;

    html += `</div>`;
    usersPagination.innerHTML = html;

    usersPagination.querySelectorAll("[data-page]").forEach((button) => {
      button.addEventListener("click", () => {
        loadUsers(Number(button.dataset.page));
      });
    });
  }

  async function loadUsers(page = 1) {
    const search = userSearchInput.value.trim();

    toggleUserLoading(true);

    try {
      const response = await fetch(
        `/api/users?search=${encodeURIComponent(search)}&page=${page}&per_page=5`
      );
      const data = await response.json();

      if (!response.ok || !data.success) {
        usersTableBody.innerHTML = `
          <tr>
            <td colspan="5" class="table-empty">Failed to load users.</td>
          </tr>
        `;
        usersPagination.innerHTML = "";
        return;
      }

      renderUserRows(data.data || []);
      renderUserPagination(data.page || 1, data.pages || 1);
    } catch (error) {
      usersTableBody.innerHTML = `
        <tr>
          <td colspan="5" class="table-empty">Something went wrong while loading users.</td>
        </tr>
      `;
      usersPagination.innerHTML = "";
    } finally {
      toggleUserLoading(false);
    }
  }

  userSearchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    loadUsers(1);
  });

  clearUserSearchBtn.addEventListener("click", () => {
    userSearchInput.value = "";
    loadUsers(1);
  });
});