function checkAndSubmit() {
    var imageToEdit = document.getElementById('image_to_edit');
    if (imageToEdit.children.length > 0) {
        var selectedImage = imageToEdit.children[0];
        var photoId = selectedImage.getAttribute('data-photo-id');

        var formData = new FormData(document.getElementById('myForm'));
        var photoModel = selectedImage.getAttribute('data-photo-model');

        formData.append('photo_id', photoId);
        formData.append('photo_model', photoModel);


        fetch(document.getElementById('myForm').action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('changed_img').innerHTML = '<img src="' + data.changed_image_url + '" alt="Changed Image" style="max-height: 200px">';
            var imagetoimage = document.createElement('img');
            imagetoimage.src = data.changed_image_url;
            imagetoimage.alt = 'changed image';
            imagetoimage.style = 'max-height: 100px';
            document.getElementById('iti_image_from_base').appendChild(imagetoimage);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    } else{
        alert('Add image before running the script.');
    }
}



function moveImageToEdit(imgElement, sourceContainerId, targetContainerId) {
    var sourceContainer = document.getElementById(sourceContainerId);
    var targetContainer = document.getElementById(targetContainerId);
    var changedImgContainer = document.getElementById('changed_img');

    if (targetContainer.children.length > 0) return;

    sourceContainer.removeChild(imgElement);
    imgElement.style.maxHeight = '200px';

    imgElement.onclick = function() {
        changedImgContainer.innerHTML = '';
        sourceContainer.appendChild(imgElement);
        imgElement.style.maxHeight = '100px';
        imgElement.onclick = function() {
            moveImageToEdit(this, sourceContainerId, targetContainerId);
        };
    };

    targetContainer.appendChild(imgElement);
}


    document.getElementById('myForm').addEventListener('submit', function (event) {
        event.preventDefault();
    });


    function generateRandomSeed() {
    var randomSeed = Math.floor(Math.random() * 1000000000) + 1;
    document.getElementById("seed_input").value = randomSeed;
}

var guidanceSlider = document.getElementById("guidance_scale_input");
var guidanceOutput = document.querySelector("output[for=guidance_scale_input]");

var strengthSlider = document.getElementById("strength_scale_input");
var strengthOutput = document.querySelector("output[for=strength_scale_input]");

guidanceSlider.addEventListener("input", function() {
    guidanceOutput.textContent = guidanceSlider.value;
});

guidanceSlider.addEventListener("change", function() {
    guidanceOutput.textContent = guidanceSlider.value;
});

strengthSlider.addEventListener("input", function() {
    strengthOutput.textContent = strengthSlider.value;
});

strengthSlider.addEventListener("change", function() {
    strengthOutput.textContent = strengthSlider.value;
});