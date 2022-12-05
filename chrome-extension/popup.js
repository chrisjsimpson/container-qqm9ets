let editSite = document.getElementById("editSite");
let savePreview = document.getElementById("savePreview");

// When the savePreview button is clicked, save the document and upload it somewhere for preview
savePreview.addEventListener("click", async () => {
  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    function: savePagePreview,
  });
});

// The body of this function will be executed as a content script inside the
// current page
function setPageContentEditable() {
  document.body.contentEditable = "true";
  alert("You can now edit any text on this page.");
}

// Save Page preview and generate share url
function savePagePreview() {
  console.log(document.documentElement.innerText);

  let body = document.body.innerText;

	fetch('https://save-chatgpt.anotherwebservice.com/save', {
		method: 'POST',
		body: JSON.stringify({
			body: body
		}),
		headers: {
			'Content-Type': 'application/json'
		}
	})
		.then(response => response.json())
		.then(data => {
			console.log(data);
      let url = "https://save-chatgpt.anotherwebservice.com/chat/" + data['file_id'];
      console.log("Opening: " + url);
		  window.open(url);
		});


}
