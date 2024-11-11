function toggleCommentForm(event) {
    const x = document.getElementById(`toggle-comment-form-${event.target.value}`);
    if (x.style.display !== "block") {
      x.style.display = "block";
      event.target.innerHTML = "Hide"
    } else {
      x.style.display = "none";
      event.target.innerHTML = "Reply"
    }
  }
