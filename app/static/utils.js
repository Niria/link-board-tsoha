function toggleThreadLike(event) {
  const url = event.target.dataset.url;
  const image = document.getElementById('thumb');
  image.classList.toggle('thumb-active');
  const csrf_token = event.target.dataset.csrf;

  fetch(url, {
    method: "POST",
    headers: {
      "Content-type": "application/json",
      "X-CSRFToken": csrf_token,
    }
  })
      .then((response) => response.json())
      .then((json) => event.target.querySelector('#thread-likes').innerHTML = json.likes);
}

function toggleReplyLike(reply) {
  const url = reply.dataset.url;
  const csrf_token = reply.dataset.csrf;
  const image = reply.querySelector('#thumb');
  image.classList.toggle('thumb-active');

  fetch(url, {
    method: "POST",
    headers: {
      "Content-type": "application/json",
      "X-CSRFToken": csrf_token
    }
  })
      .then((response) => response.json())
      .then((json) => reply.querySelector('#reply-likes').innerHTML = json.likes);
}

function toggleUserFollow(follow) {
  const user_id = follow.dataset.user_id;
  const url = follow.dataset.url;
  const csrf_token = follow.dataset.csrf;

  fetch(url, {
    method: "POST",
    headers: {
      "Content-type": "application/json",
      "X-CSRFToken": csrf_token
    }
  })
      .then((response) => response.json())
      .then((json) => {
        follow.innerHTML = json.following ? 'Following' : 'Follow';
        follow.classList.toggle('following');
      })
}

function toggleCategoryFavourite(favourite) {
  const url = favourite.dataset.url;
  const csrf_token = favourite.dataset.csrf;
  const user_id = favourite.dataset.user_id;

  fetch(url, {
    method: "POST",
    headers: {
      "Content-type": "application/json",
      "X-CSRFToken": csrf_token
    }
  })
      .then((response) => response.json())
      .then((json) => {
        favourite.style.fill = json.favourite ? 'gold' : 'none';
      })
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
      const replyComment = reply.querySelectorAll('.toggle-comment-form');
      if (replyComment.length > 0) {
        reply.querySelector('.form-toggle').addEventListener('click', () => {
          replyComment[0].classList.toggle('hidden');
          if (!replyComment[1].classList.contains('hidden')) {
            replyComment[1].classList.toggle('hidden');
          }
        })
        const editReply = reply.querySelector('.form-toggle-edit')
        if (editReply !== null) {
          editReply.addEventListener('click', () => {
            const existingComment = reply.querySelector('.reply-message');
            replyComment[1].querySelector('textarea').innerHTML = existingComment.innerHTML;
            replyComment[1].classList.toggle('hidden');
            if (!replyComment[0].classList.contains('hidden')) {
              replyComment[0].classList.toggle('hidden');
            }
        })
        }

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

  // Initialize eventListener for favouriting category
  const categoryFavourite = document.querySelector('#category-favourite');
  if (categoryFavourite !== null) {
    categoryFavourite.addEventListener('click', () => toggleCategoryFavourite(categoryFavourite));
  }

  // Initialize eventListener for closing messages
  const messages = document.querySelector('.messages');
  if (messages !== null) {
    messages.addEventListener('click', () => messages.remove())
  }
}

document.addEventListener('DOMContentLoaded', () => setEventHandlers())
