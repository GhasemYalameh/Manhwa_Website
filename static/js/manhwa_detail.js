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
                text: comment_text,
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
                                 <div class="reactions">
                                    <button class="reaction-btn like-btn" onclick="reactionHandler(${data.comment_id}, 'lk')">
                                        <svg class="icon-like comment-like-${data.comment_id}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M7 22H4C3.46957 22 2.96086 21.7893 2.58579 21.4142C2.21071 21.0391 2 20.5304 2 20V13C2 12.4696 2.21071 11.9609 2.58579 11.5858C2.96086 11.2107 3.46957 11 4 11H7M14 9V5C14 4.20435 13.6839 3.44129 13.1213 2.87868C12.5587 2.31607 11.7956 2 11 2L7 11V22H18.28C18.7623 22.0055 19.2304 21.8364 19.5979 21.524C19.9654 21.2116 20.2077 20.7769 20.28 20.3L21.66 11.3C21.7035 11.0134 21.6842 10.7207 21.6033 10.4423C21.5225 10.1638 21.3821 9.90629 21.1919 9.68751C21.0016 9.46873 20.7661 9.29393 20.5016 9.17522C20.2371 9.0565 19.9499 8.99672 19.66 9H14Z"/>
                                        </svg>
                                        <span class="count" id="likeCount-${data.comment_id}">0</span>
                                    </button>
                                    <button class="reaction-btn dislike-btn" onclick="reactionHandler(${data.comment_id},'dlk')">
                                        <svg class="icon-dislike comment-dislike-${data.comment_id}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 2H20C20.5304 2 21.0391 2.21071 21.4142 2.58579C21.7893 2.96086 22 3.46957 22 4V11C22 11.5304 21.7893 12.0391 21.4142 12.4142C21.0391 12.7893 20.5304 13 20 13H17M10 15V19C10 19.7956 10.3161 20.5587 10.8787 21.1213C11.4413 21.6839 12.2044 22 13 22L17 13V2H5.72C5.23767 1.99451 4.76962 2.16361 4.40213 2.47596C4.03464 2.78831 3.79234 3.22307 3.72 3.7L2.34 12.7C2.29649 12.9866 2.31583 13.2793 2.39668 13.5577C2.47753 13.8362 2.61793 14.0937 2.80814 14.3125C2.99835 14.5313 3.23394 14.7061 3.49843 14.8248C3.76291 14.9435 4.05009 15.0033 4.34 15H10Z"/></svg>
                                        <span class="count" id="dislikeCount-${data.comment_id}">0</span>
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
