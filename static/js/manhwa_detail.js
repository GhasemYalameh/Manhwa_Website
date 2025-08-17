const form = document.getElementById('comment-form');
const comments_list = document.getElementById('comments-list');

let isCommentsLoaded = false;

let mainCommentId = null;

// form info
const path_names = window.location.pathname.split('/');
const manhwa_id = path_names[path_names.length - 2];
const comment_text = document.getElementById('id_text').value;

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


document.addEventListener('DOMContentLoaded', async function (){
    const response = await fetch(`/api/manhwas/${manhwa_id}/set_view/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': get_csrf_token()
        },
    })

    const data = await response.json();
})

function setStyleNone(toNone, toBlock){
    const translate = {
        'tab-detail': 'detail',
        'tab-episodes': 'episodes',
        'tab-comments': 'comments'
    }
    const toNoneDiv = document.querySelector(`.${translate[toNone]}`)
    const toBlockDiv = document.querySelector(`.${translate[toBlock]}`)
    toNoneDiv.style.display = 'none'
    toBlockDiv.style.display = 'block'
}

async function load_comments(){
    if (isCommentsLoaded) return;

    const response = await fetch(
        `/detail/${manhwa_id}/`,{
            method: 'GET',
            headers: {
                'Tab-Load': 'comments'
            }
        })
    const data = await response.json()
    document.querySelector('.comment-list').innerHTML = data.html
    isCommentsLoaded = true
}

document.querySelector('.tabs').addEventListener('click', async function (e){
    const tab = e.target.closest('.tab')
    const lastTab = document.querySelector('.tab-active')
    if (tab.classList.contains('tab-comments')){
        await load_comments()
    }
    lastTab.classList.remove('tab-active')
    tab.classList.add('tab-active')
    setStyleNone(lastTab.classList[1], tab.classList[1])

})

form.addEventListener('submit', async function(e){
    e.preventDefault()

    const comment_text = document.getElementById('id_text').value

    const response = await fetch(
        `/api/manhwas/${manhwa_id}/comments/`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': get_csrf_token()
            },
            body: JSON.stringify({
                'text': comment_text,
                'parent': mainCommentId===null ? null:mainCommentId
            })
        })

    const data = await response.json()  // if success: data is comment data

    if (response.ok){
        if (mainCommentId===null){
            const comment_data = data.comment
            const newComment = document.createElement('div');
            newComment.classList.add('comment-box');
            newComment.innerHTML = `
                <div class="comment-img">
                </div>
                <div class="comment-content" data-comment-id="${comment_data.id}">
                    <h3>${comment_data.author }</h3>
                    <p>${comment_data.text.replace(/\n/g, '<br>')}</p>
                    <div class="comment-bottom">
<!--                        <span>${comment_data.datetime_modified}</span>-->
                         <div class="reactions">
                            <button class="reaction-btn like-btn" data-reaction-type="lk">
                                <svg class="icon-like" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M7 22H4C3.46957 22 2.96086 21.7893 2.58579 21.4142C2.21071 21.0391 2 20.5304 2 20V13C2 12.4696 2.21071 11.9609 2.58579 11.5858C2.96086 11.2107 3.46957 11 4 11H7M14 9V5C14 4.20435 13.6839 3.44129 13.1213 2.87868C12.5587 2.31607 11.7956 2 11 2L7 11V22H18.28C18.7623 22.0055 19.2304 21.8364 19.5979 21.524C19.9654 21.2116 20.2077 20.7769 20.28 20.3L21.66 11.3C21.7035 11.0134 21.6842 10.7207 21.6033 10.4423C21.5225 10.1638 21.3821 9.90629 21.1919 9.68751C21.0016 9.46873 20.7661 9.29393 20.5016 9.17522C20.2371 9.0565 19.9499 8.99672 19.66 9H14Z"/>
                                </svg>
                                <span class="count">0</span>
                            </button>
                            <button class="reaction-btn dislike-btn" data-reaction-type="dlk">
                                <svg class="icon-dislike" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 2H20C20.5304 2 21.0391 2.21071 21.4142 2.58579C21.7893 2.96086 22 3.46957 22 4V11C22 11.5304 21.7893 12.0391 21.4142 12.4142C21.0391 12.7893 20.5304 13 20 13H17M10 15V19C10 19.7956 10.3161 20.5587 10.8787 21.1213C11.4413 21.6839 12.2044 22 13 22L17 13V2H5.72C5.23767 1.99451 4.76962 2.16361 4.40213 2.47596C4.03464 2.78831 3.79234 3.22307 3.72 3.7L2.34 12.7C2.29649 12.9866 2.31583 13.2793 2.39668 13.5577C2.47753 13.8362 2.61793 14.0937 2.80814 14.3125C2.99835 14.5313 3.23394 14.7061 3.49843 14.8248C3.76291 14.9435 4.05009 15.0033 4.34 15H10Z"/></svg>
                                <span class="count">0</span>
                            </button>
                            <button class="reaction-btn reply-btn" data-reaction-type="reply">
                                <svg width="20px" height="20px" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                                    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
                                </svg>
                                <span class="count">0</span>
                            </button>
                            <form action="/detail/${manhwa_id}/show-replied-comment/" method="post">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${get_csrf_token()}">
                                <input type="hidden" name="comment_id" value="${comment_data.id}">
                                <button type="submit">show replies</button>
                            </form>
                        </div>
                    </div>
                </div>
            `;
            document.querySelector('.comment-list').prepend(newComment);
        }
        else{
            document.querySelector('.reply-container').style.display = 'none'
            document.querySelector('#main-comment-text').textContent = ""
            document.querySelector('#main-comment-author').textContent = ""
            mainCommentId = null
        }

        document.getElementById('id_text').value = ""
    }
    // message success not in response !!
    showMessage(response.ok ? 'success':'error', data)
})

function replyForm(target){
    const replyContainer = document.querySelector('.reply-container')
    const textArea = document.querySelector('.text-area')
    const commentForm = document.querySelector('#up-form')
    const commentContent = target.closest('.comment-content')
    const commentText = commentContent.querySelectorAll('p')
    const commentAuthor = commentContent.querySelector('h3')

    let text = ""
    commentText.forEach(p => {
        if (p.textContent && text.length < 50) {
            text += p.textContent + ' '
        }
    })

    document.querySelector('#main-comment-text').textContent = text.length > 50 ? text.substring(0, 50) + '...' : text
    document.querySelector('#main-comment-author').textContent = commentAuthor.textContent
    replyContainer.style.display = 'flex'

    commentForm.scrollIntoView({
        behavior: "smooth",
        block: 'start',
        inline: "nearest"
    })
    textArea.focus()
    mainCommentId = commentContent.dataset.commentId

}

function cancelReply(){
    let replyContainer = document.querySelector('.reply-container')
    replyContainer.style.display = 'none'
    mainCommentId = null
}

document.querySelector('.comment-list').addEventListener('click', async function(e){
    const btn = e.target.closest('.reaction-btn'); // clicked btn
    if (!btn) return;

    // datas
    const commentId = btn.closest('.comment-content').dataset.commentId;
    const reaction = btn.dataset.reactionType;
    if (reaction === 'reply') return replyForm(e.target);

    const oppositeBtn = (reaction === 'lk')  // other reaction btn
            ? btn.closest('.reactions').querySelector('.dislike-btn')
            : btn.closest('.reactions').querySelector('.like-btn')

    // elements
    const svg = btn.querySelector('svg');
    const span = btn.querySelector('span');
    const oppositeSpan = oppositeBtn.querySelector('span');
    const oppositeSvg = oppositeBtn.querySelector('svg');

    const reactionDiv = btn.closest('.reactions');
    const isLikeActive = reactionDiv.querySelector('.like-btn svg').classList.contains('active');
    const isDisLikeActive = reactionDiv.querySelector('.dislike-btn svg').classList.contains('active');


    let action = null;
    let last_reaction = null;
    if (isLikeActive) last_reaction = 'lk';
    else if (isDisLikeActive) last_reaction = 'dlk';

    if (last_reaction === reaction){ // delete reaction
        const intSpan = +span.textContent;
        span.textContent = intSpan - 1;
        svg.classList.remove('active');
        action = 'delete';

    }else if (last_reaction !== reaction && last_reaction !== null){ // change reaction
        const intSpan = +span.textContent;  // current must increase
        span.textContent = intSpan + 1;
        svg.classList.add('active');

        const intOtherSpan = +oppositeSpan.textContent ; // other span must decrease
        oppositeSpan.textContent = intOtherSpan - 1;
        oppositeSvg.classList.remove('active');

        action = 'change';

    }else if (last_reaction === null){  // add reaction
        const intSpan = +span.textContent ; // current reaction must increase
        span.textContent = intSpan + 1;
        svg.classList.add('active');

        action = 'add';
    }

    const response = await fetch(
        '/api/comment-reaction/',{
            method: 'POST',
            headers:{
                'Content-Type': 'application/json',
                'X-CSRFToken': get_csrf_token()
            },
            body: JSON.stringify({
                'reaction': reaction,
                'comment_id': commentId
            })

        }
    )
    const data = await response.json();
    if (response.ok){
        const likesCount = data.comment.likes_count;
        const disLikesCount = data.comment.dis_likes_count;

        // update this reaction btn
        span.textContent = (reaction === 'lk') ? likesCount : disLikesCount;

        // update opposite btn
        oppositeSpan.textContent = (reaction === 'lk') ? disLikesCount : likesCount;

    }else{
        // back reaction UI
        reverseUI();
    }

    function reverseUI(){
        if (action === 'add'){
            svg.classList.remove('active');

        }else if (action === 'change'){
            svg.classList.remove('active');
            oppositeSvg.classList.add('active');

        }else if (action === 'delete'){
            svg.classList.add('active');
        }
    }
})

function  showMessage(message_type, data){

    const errorDiv = document.getElementById('form-error-messages');
    errorDiv.innerHTML = ''; // delete last errors

    if (message_type === 'success'){
        const messageList = document.querySelector('.messages');
        const li = document.createElement('li');
        li.className = message_type;
        li.textContent = data.message
        messageList.appendChild(li)

        setTimeout(() => {
            li.remove()
        }, 2000)
    }
    else if (message_type === 'error'){
        const ul = document.createElement('ul');
        ul.style.color = 'red';

        for (const [field, errorList] of Object.entries(data)){
            errorList.forEach(errorMsg => {
                const li = document.createElement('li');

                if (field === 'non_field_errors'){
                    li.textContent = errorMsg;
                }
                else{
                    li.textContent = `${field}: ${errorMsg}`
                }

                ul.appendChild(li)
            })
        }
        errorDiv.appendChild(ul)
    }
}
