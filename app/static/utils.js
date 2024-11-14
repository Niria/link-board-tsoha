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

function likeReply(reply) {
  const url = reply.dataset.url;
  const csrf_token = JSON.parse(reply.dataset.csrf);
  const image = reply.querySelector('#thumb');
  image.classList.toggle('thumbactive');
  fetch(url, {
    method: "POST",
    headers: {
      "Content-type": "application/json",
      "csrf-token": csrf_token
    }
  })
    .then((response) => response.json())
    .then((json) => reply.querySelector('#reply-likes').innerHTML = `${json.likes} likes`);
}

function setEventHandlers() {
  // Initialize eventListener for thread clicks
  const threadContent = document.querySelector('.thread-content')
  if ( threadContent !== null) {
    const threadComment = threadContent.querySelector('.toggle-comment-form')
    threadContent.querySelector('.form-toggle').addEventListener('click', () => {
      threadComment.classList.toggle('hidden')
    })
    threadContent.querySelector('#like-thread').addEventListener('click', likeThread)
  }

  // Initialize eventlisteners for replies clicks
  const replyContent = document.querySelectorAll('.reply-content')
  if (replyContent !== null) {
    replyContent.forEach((reply) => {
      const replyComment = reply.querySelector('.toggle-comment-form');
      if (replyComment !== null) {
        reply.querySelector('.form-toggle').addEventListener('click', () => {
          replyComment.classList.toggle('hidden')
        })
      }
      const replyLike = reply.querySelector('#like-reply')
      replyLike.addEventListener('click', () => likeReply(reply))
    })
  }
}

document.addEventListener('DOMContentLoaded', () => setEventHandlers())
