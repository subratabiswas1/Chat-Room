let $ = jQuery;
let socket;

function initializeWebSocket() {
  socket = new WebSocket('http://0.0.0.0:10000//message');

  socket.onopen = function (event) {
    socket.send(JSON.stringify({"message": "Have joined!!","username": $('#usernameInput').val()}));
    console.log('WebSocket connection established.');
  };

  socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    const msgClass = data.isMe ? 'user-message' : 'other-message';
    const sender = data.isMe ? 'You' : data.username;
    const message = data.data;
    const messageElement = $('<li>').addClass('clearfix');

    if(message == " have joined!!"){
        data.isMe ? messageElement.append($('<div>').addClass('join-message-user').text(sender + message))
        : messageElement.append($('<div>').addClass('join-message-other').text(sender + message))
    }
    else{
        messageElement.append($('<div>').addClass(msgClass).text(sender + ': ' + message));
    }
    $('#messages').append(messageElement);
    $('#chat').scrollTop($('#chat')[0].scrollHeight);
  };

  socket.onerror = function (event) {
    // socket.send(JSON.stringify({"message": " has left the room"}));
    console.error('WebSocket error. Please rejoin the chat.');
    showJoinModal();
  };

  socket.onclose = function (event) {
    // socket.send(JSON.stringify({"message": " has left the room"}));
    if (event.code === 1000) {
      console.log('WebSocket closed normally.');
    } else {
      console.error('WebSocket closed with error code: ' + event.code + '. Please rejoin the chat.');
      showJoinModal();
    }
  };
}

function showJoinModal() {
  $('#username-form').show();
  $('#chat').hide();
  $('#message-input').hide();
  $('#usernameModal').modal('show');
}

$('#open-modal').click(function () {
  showJoinModal();
});

function joinChat() {
  $('#username-form').hide();
  $('#chat').show();
  $('#message-input').show();
  $('#usernameModal').modal('hide');
}

$('#join').click(function () {
  initializeWebSocket();
  joinChat();
});

$('#send').click(function () {
  sendMessage();
});

$('#message').keydown(function (event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});

function sendMessage() {
  const message = $('#message').val();
  if (message) {
    socket.send(JSON.stringify({ "message": message, "username": $('#usernameInput').val() }));
    $('#message').val('');
  }
}