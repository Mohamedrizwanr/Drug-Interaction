const rec = new webkitSpeechRecognition();
rec.lang = "en-US";

function startVoice() {
  rec.start();
}

rec.onresult = e => {
  document.getElementById("drugInput").value +=
    ", " + e.results[0][0].transcript;
};
