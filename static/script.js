document.getElementById("upload-box").addEventListener("click", function() {
    document.getElementById("imageUpload").click();
});

document.getElementById("imageUpload").addEventListener("change", function() {
    document.querySelector(".upload-box p").innerText = "File Selected: " + this.files[0].name;
});

function uploadImage() {
    let fileInput = document.getElementById("imageUpload");
    if (fileInput.files.length === 0) {
        alert("Please select an image.");
        return;
    }

    let formData = new FormData();
    formData.append("image", fileInput.files[0]);

    let progressBar = document.getElementById("progress-bar");
    let progress = document.querySelector(".progress");
    progressBar.style.display = "block";
    progress.style.width = "0%";

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        progress.style.width = "100%";

        if (data.error) {
            alert(data.error);
        } else {
            let outputDiv = document.getElementById("output");
            outputDiv.textContent = JSON.stringify(data.extracted_data, null, 2);

            let downloadLink = document.getElementById("downloadLink");
            downloadLink.href = data.download_link;
            downloadLink.style.display = "block";
            downloadLink.textContent = "Download Extracted Data";
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}