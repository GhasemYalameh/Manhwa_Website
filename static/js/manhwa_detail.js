const form = document.getElementById('comment-form')
const comments_list = document.getElementById('comments-list')

// form info
const path_names = window.location.pathname.split('/')
const manhwa_id = path_names[path_names.length - 2]
const comment_text = document.getElementById('id_text').value

function get_csrf_token(){
    let cookieValue = null
    if (document.cookie && document.cookie!==''){
        const cookie = document.cookie.split(';')
        for (const cookieItem of cookie){
            const cookie = cookieItem.trim()
            if (cookie.substring(0, 10)===('csrftoken=')){
                cookieValue = decodeURIComponent(cookie.substring(10))
            }
        }
    }
    return cookieValue
}

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
                            <h3>${data.author}</h3>
                            <p>${data.body}</p>
                            <span>${data.datetime_modified}</span>
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

