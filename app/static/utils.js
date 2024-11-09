function toggleCommentForm(event) {
    console.log(event)
    var x = document.getElementById(`toggle-comment-form-${event.target.value}`);
    console.log(x.style.display)
    if (x.style.display !== "block") {
      x.style.display = "block";
      event.target.innerHTML = "Hide"
    } else {
      x.style.display = "none";
      event.target.innerHTML = "Reply"
    }
  }
