"use strict"

// Function to create the profile link HTML
function makeProfileLinkHTML(post) {
    if (post.user_id == requestUserId) {
        // If the post was made by the logged-in user, link to the user's own profile
        return `<a href="${myProfileUrl}" class="post_profile" id="id_post_profile_${post.id}">${post.fname} ${post.lname}</a>`;
    } else {
        // If the post was made by a different user, link to that user's profile
        return `<a href="${userProfileUrlTemplate + post.user_id}" class="post_profile" id="id_post_profile_${post.id}">${post.fname} ${post.lname}</a>`;
    }
}

// Function to create the datetime HTML
function makeDateTimeHTML(post) {
    let dateTime = new Date(post.creation_time);
    let date = dateTime.toLocaleDateString('en-US');
    let time = dateTime.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });

    // Split the time by the separator (":") and the space before AM/PM, then reconstruct it.
    let [hour, minutePart] = time.split(':');
    let [minute, amPm] = minutePart.split(' ');

    // Remove leading zero from the minute if it exists
    minute = parseInt(minute, 10).toString();

    // Reconstruct the time string with the modified minute
    time = `${hour}:${minute} ${amPm}`;
    return `<span class="post_date_time" id="id_post_date_time_${post.id}">${date} ${time}</span>`;
}


// Function to create the post HTML
function makePostHTML(post, comments) {
    let commentHTML = comments.map(makeCommentHTML).join('');

    return `<div class="post_div" id="id_post_div_${post.id}">
                ${makeProfileLinkHTML(post)}:
                <span id="id_post_text_${post.id}">${post.text}</span>
                ${makeDateTimeHTML(post)}
                <div class="comment_container" id="comments_for_post_${post.id}">
                    ${commentHTML}
                </div>
                ${makeNewCommentBoxHTML(post)}
            </div>`;
}

function makeCommentProfileLinkHTML(comment) {
    if (comment.user_id == requestUserId) {
        // If the comment was made by the logged-in user, link to the user's own profile
        return `<a href="${myProfileUrl}" class="comment_profile" id="id_comment_profile_${comment.id}">${comment.fname} ${comment.lname}</a>`;
    } else {
        // If the comment was made by a different user, link to that user's profile
        return `<a href="${userProfileUrlTemplate + comment.user_id}" class="comment_profile" id="id_comment_profile_${comment.id}">${comment.fname} ${comment.lname}</a>`;
    }
}


function makeCommentDateTimeHTML(comment) {
    let dateTime = new Date(comment.creation_time);
    let date = dateTime.toLocaleDateString('en-US');
    let time = dateTime.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });

    // Split the time by the separator (":") and the space before AM/PM, then reconstruct it.
    let [hour, minutePart] = time.split(':');
    let [minute, amPm] = minutePart.split(' ');

    // Remove leading zero from the minute if it exists
    minute = parseInt(minute, 10).toString();

    // Reconstruct the time string with the modified minute
    time = `${hour}:${minute} ${amPm}`;
    return `<span class="comment_date_time" id="id_comment_date_time_${comment.id}">${date} ${time}</span>`;
}

function makeCommentHTML(comment) {
    return `<div class="comment_div" id="id_comment_div_${comment.id}">
                            ${makeCommentProfileLinkHTML(comment)}:
                            <span id="id_comment_text_${comment.id}">${comment.text}</span>
                            ${makeCommentDateTimeHTML(comment)}
            </div>`;
}

// Function to create the new comment box HTML
function makeNewCommentBoxHTML(post) {
    return `
        <div class="comment_input">
            <label for="id_comment_input_text_${post.id}">New Comment:</label>
            <input class="comment_input_text" type="text" id="id_comment_input_text_${post.id}" name="comment_n">
            <button onclick="addComment(${post.id})" class="comment_button" id="id_comment_button_${post.id}" type="submit">Comment</button>
        </div>
    `;
}

// Function to insert the post into the DOM
function insertPost(postHTML) {
    let postContentDiv = document.getElementById('post-content');
    postContentDiv.insertAdjacentHTML('afterbegin', postHTML);
}

function insertComment(commentHTML, postId) {
    let commentContainerId = `comments_for_post_${postId}`;

    let commentContainerDiv = document.getElementById(commentContainerId);

    // Check if the container exists to avoid null reference errors
    if (commentContainerDiv) {
        // Insert the comment HTML at the end of the container
        commentContainerDiv.insertAdjacentHTML('beforeend', commentHTML);
    } else {
        // If the container doesn't exist, you might want to log an error or handle it appropriately
        console.error(`Comment container not found for post ID: ${postId}`);
    }
}
////////////////////////////////////////

// Sends a new request to update the to-do list
function getPost() {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updatePage(xhr)
    }

    xhr.open("GET", getGlobalURL, true)
    xhr.send()
}

function getFollowerPost() {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updatePage(xhr)
    }

    xhr.open("GET", getFollowerURL, true)
    xhr.send()
}

// Function to update comments for a post
function updateComments(postComments, commentContainerDiv) {
    // Get all existing comment IDs for the post
    let existingCommentIds = Array.from(commentContainerDiv.querySelectorAll('.comment_div'))
                                 .map(div => parseInt(div.id.replace('id_comment_div_', ''), 10));

    // Insert new comments
    postComments.forEach(comment => {
        if (!existingCommentIds.includes(comment.id)) {
            let commentHTML = makeCommentHTML(comment);
            insertComment(commentHTML, comment.post_id);
        }
    });
}
function updatePage(xhr) {
    if (xhr.status === 0) {
        displayError("Cannot connect to server")
        return
    }

    // Now it's safe to parse the JSON response
    let response = JSON.parse(xhr.responseText);

    // Handle any application-level errors reported in the response
    if (response.hasOwnProperty('error')) {
        displayError(response.error);
        return;
    }
    if (xhr.status === 200 && response.hasOwnProperty('comment')) {
        let newComment = response.comment;
        let commentHTML = makeCommentHTML(newComment);
        insertComment(commentHTML, newComment.post_id);
        return;
    }

    if (xhr.status === 200 && response.hasOwnProperty('posts')) {
        let posts = response['posts'];
        let comments = response['comments'] || [];
        // Get all existing post IDs in the DOM
        let existingPostIds = Array.from(document.querySelectorAll('.post_div'))
                                  .map(div => div.id.replace('id_post_div_', ''));

        // Iterate in reverse if the newest posts are at the end of the array
        for (let i = posts.length - 1; i >= 0; i--) {
            let post = posts[i];
            let postComments = comments.filter(comment => comment.post_id === post.id);

            let postDiv = document.getElementById(`id_post_div_${post.id}`);
            let commentContainerDiv = document.getElementById(`comments_for_post_${post.id}`);
            if (postDiv && commentContainerDiv) {
                updateComments(postComments, commentContainerDiv);
            } else{
                if (!existingPostIds.includes(String(post.id))) {
                    let postHTML = makePostHTML(post, postComments);
                    insertPost(postHTML); // Prepend the new post HTML
                }
            }
        }
    }
}

function displayError(message) {
    let errorElement = document.getElementById("error");
    if (errorElement) {
        errorElement.innerHTML = message;
    } else {
        console.error('Error element not found on the page.');
    }
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown"
}

function addComment(postId) {
    let itemTextElement = document.getElementById(`id_comment_input_text_${postId}`);
    if (!itemTextElement) {
        displayError('Comment input element not found');
        return;
    }
    let commentTextValue = itemTextElement.value;
    if (commentTextValue === '') {
        displayError('Comment text cannot be empty.');
        return;
    }
    itemTextElement.value = ''; // Clear the input box after grabbing the value

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return;

        if (xhr.status === 200) {
            // Handle successful AJAX response
            updatePage(xhr);
        } else if (xhr.status === 400) {
            displayError('Bad request. Please check your input and try again.');
        } else if (xhr.status === 401) {
            displayError('You must be logged in to post comments.');
        } else if (xhr.status === 403) {
            displayError('Forbidden. Invalid CSRF token or action not allowed.');
        } else if (xhr.status === 405) {
            displayError('Invalid method. Please contact support.');
        } else {
            try {
                let response = JSON.parse(xhr.responseText);
                displayError(response.error || 'An unknown error occurred.');
            } catch (e) {
                displayError('Failed to parse error response.');
            }
        }
    };

    let csrfToken = getCSRFToken();
    if (csrfToken === "unknown") {
        displayError('CSRF token not found. Please refresh the page.');
        return;
    }

    let requestData = `comment_text=${encodeURIComponent(commentTextValue)}&post_id=${encodeURIComponent(postId)}&csrfmiddlewaretoken=${csrfToken}`;

    xhr.open("POST", '/pawconnect/add-comment', true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send(requestData);
}