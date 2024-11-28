function toggleThreadLike(event) {
  const url = event.target.dataset.url;
  const csrf_token = JSON.parse(event.target.dataset.csrf);
  const image = document.getElementById('thumb');
  image.classList.toggle('thumb-active');

  fetch(url, {
    method: "POST",
    headers: {
      "Content-type": "application/json",
      "csrf-token": csrf_token
    }
  })
      .then((response) => response.json())
      .then((json) => event.target.querySelector('#thread-likes').innerHTML = json.likes);
}

function toggleReplyLike(reply) {
  const url = reply.dataset.url;
  const csrf_token = JSON.parse(reply.dataset.csrf);
  const image = reply.querySelector('#thumb');
  image.classList.toggle('thumb-active');
  fetch(url, {
    method: "POST",
    headers: {
      "Content-type": "application/json",
      "csrf-token": csrf_token
    }
  })
      .then((response) => response.json())
      .then((json) => reply.querySelector('#reply-likes').innerHTML = json.likes);
}

function toggleUserFollow(follow) {
  const url = follow.dataset.url;
  const csrf_token = JSON.parse(follow.dataset.csrf);
  fetch(url, {
    method: "POST",
    headers: {
      "Content-type": "application/json",
      "csrf-token": csrf_token
    }
  })
      .then((response) => response.json())
      .then((json) =>
          follow.innerHTML = json.following ? 'Following' : 'Follow');
          follow.classList.toggle('following');
}


function setEventHandlers() {
  // Initialize eventListener for thread clicks
  const threadContent = document.querySelector('.thread-content');
  if (threadContent !== null) {
    const threadComment = threadContent.querySelector('.toggle-comment-form');
    threadContent.querySelector('.form-toggle').addEventListener('click', () => {
      threadComment.classList.toggle('hidden');
    })
    threadContent.querySelector('#like-thread').addEventListener('click', (e) => toggleThreadLike(e));
  }

  // Initialize eventlisteners for reply clicks
  const replyContent = document.querySelectorAll('.reply-content-container');
  if (replyContent !== null) {
    replyContent.forEach((reply) => {
      const replyComment = reply.querySelector('.toggle-comment-form');
      if (replyComment !== null) {
        reply.querySelector('.form-toggle').addEventListener('click', () => {
          replyComment.classList.toggle('hidden');
        })
      }
      const likeReply = reply.querySelector('#like-reply');
      likeReply.addEventListener('click', () => toggleReplyLike(likeReply));
    })
  }

  // Initialize eventListener for following user
  const userFollow = document.querySelector('#user-follow');
  if (userFollow !== null) {
    userFollow.addEventListener('click', () => toggleUserFollow(userFollow));
  }
}

document.addEventListener('DOMContentLoaded', () => setEventHandlers())
