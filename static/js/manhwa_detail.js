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
                const new_comment = `
                    <div class="comment-box">
                        <div class="comment-img">
                        </div>
                        <div class="comment-content">
                            <h3>${data.author_name }</h3>
                            <p>${data.body}</p>
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
                    </div>
                `
                const currentCommentsList = document.getElementById('comments-list')
                document.getElementById('comments-list').innerHTML =
                    new_comment + currentCommentsList.innerHTML;


            }
            document.getElementById('id_text').value = ""

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
            changeCommentUi(comment_id, data)
        }
    })

}

function changeCommentUi(comment_id, data){
    let like_btn = document.getElementById(`comment-${comment_id}-lk-count`)
    let dislike_btn = document.getElementById(`comment-${comment_id}-dlk-count`)

    like_btn.classList.remove('active')
    dislike_btn.classList.remove('active')

    if (data.reaction === 'like'){
        like_btn.classList.add('active')
    }else if (data.reaction === 'dislike'){
        dislike_btn.classList.add('active')
    }

    like_btn.innerHTML = "lk:" + data.likes_count
    dislike_btn.innerHTML = "dlk:" + data.dis_likes_count

}
