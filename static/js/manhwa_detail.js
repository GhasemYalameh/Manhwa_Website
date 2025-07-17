const form = document.getElementById('comment-form')
const comments_list = document.getElementById('comments-list')

// form info
const path_names = window.location.pathname.split('/')
const manhwa_id = path_names[path_names.length - 2]
const comment_text = document.getElementById('id_text').value

function get_csrf_token(){
    const cookieString = document.cookie
    if (!cookieString) return null;

    const csrf_token =
        cookieString
            .split(';')
            .find(cookie => cookie.trim().startsWith('csrftoken='));

    if (!csrf_token) return null

    return csrf_token.split('=')[1]
}


document.addEventListener('DOMContentLoaded', function (){

    fetch('set-view/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': get_csrf_token()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status) console.log(data.message)
        else console.log(data.message)
    })
    .catch(error => console.error(error))
})


form.onsubmit = function (e){
    e.preventDefault() //provide refresh

    const comment_text = document.getElementById('id_text').value

    fetch(
        `/manhwa/${manhwa_id}/add-comment/`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': get_csrf_token()
            },
            body: JSON.stringify({
                body: comment_text,
            })
        })
        .then(response => response.json())
        .then( data => {
            if (data.status){

                const newComment = document.createElement('div');
                newComment.classList.add('comment-box');
                newComment.innerHTML = `
                        <div class="comment-img">
                        </div>
                        <div class="comment-content">
                            <h3>${data.author_name }</h3>
                            <p>${data.body.replace(/\n/g, '<br>')}</p>
                            <div class="comment-bottom">
                                <span>${data.datetime_modified}</span>
                                <div class="comment-reactions">
                                    <button
                                            onclick="reactionHandler(${data.comment_id}, 'lk')"
                                            id="comment-${data.comment_id}-lk-count">
                                        lk:0
                                    </button>
                                    <button
                                            onclick="reactionHandler(${data.comment_id}, 'dlk')"
                                            id="comment-${data.comment_id}-dlk-count">
                                        dlk:0
                                    </button>
                                </div>
                            </div>
                        </div>
                `;

                document.getElementById('comments-list').prepend(newComment);
                document.getElementById('id_text').value = ""

            }
            showMessage(data.status===true ? 'success':'error', data.message)
            }
        )
}

function reactionHandler(comment_id, reaction){

    fetch(`/comment-reaction/${comment_id}/`, {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': get_csrf_token()
        },
        body: JSON.stringify({
            reaction: reaction
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status){
            changeCommentUi(comment_id, data);
        }
        showMessage(data.status===true ? 'success':'error', data.message)
    })

}

function changeCommentUi(comment_id, data){
    let like_btn = document.querySelector(`.comment-like-${comment_id}`)
    let dislike_btn = document.querySelector(`.comment-dislike-${comment_id}`)

    like_btn.classList.remove('active')
    dislike_btn.classList.remove('active')

    if (data.reaction === 'like'){
        like_btn.classList.add('active')
    }else if (data.reaction === 'dislike'){
        dislike_btn.classList.add('active')
    }

    document.querySelector(`#likeCount-${comment_id}`).textContent = data.likes_count
    document.querySelector(`#dislikeCount-${comment_id}`).textContent = data.dis_likes_count

}

function  showMessage(message_type, message){
    if (!message) return ;
    const messageList = document.querySelector('.messages');
    const li = document.createElement('li');
    li.className = message_type==='success' ? 'success':'error';
    li.textContent = message;

    messageList.appendChild(li);

    setTimeout(() => {
        li.remove()
    }, 2000)


}
