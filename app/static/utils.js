function toggleCommentForm(event) {
  const form = document.getElementById(`toggle-comment-form-${event.target.dataset.replyform}`);
  if (form.style.display !== "block") {
    form.style.display = "block";
    event.target.innerHTML = "Hide"
  } else {
    form.style.display = "none";
    event.target.innerHTML = "Reply"
  }
}

function likeThread() {
  const url = document.getElementById('like-thread').dataset.url;
  const csrf_token = JSON.parse(document.getElementById('like-thread').dataset.csrf);
  const image = document.getElementById('thumb');
  image.classList.toggle('thumbactive');
  
  fetch(url, {
    method: "POST",
    headers: {
      "Content-type": "application/json",
      "csrf-token": csrf_token
    }
  })
    .then((response) => response.json())
    .then((json) => document.getElementById('thread-likes').innerHTML = `${json.likes} likes`);
}

function likeReply(reply_id) {
  const url = document.getElementById(`like-reply-${reply_id}`).dataset.url;
  const csrf_token = JSON.parse(document.getElementById(`like-reply-${reply_id}`).dataset.csrf);
  const image = document.getElementById(`thumb-${reply_id}`);
  image.classList.toggle('thumbactive');

  fetch(url, {
    method: "POST",
    headers: {
      "Content-type": "application/json",
      "csrf-token": csrf_token
    }
  })
    .then((response) => response.json())
    .then((json) => document.getElementById(`reply-likes-${reply_id}`).innerHTML = `${json.likes} likes`);
  }