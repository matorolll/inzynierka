function checkAndSubmit() {
    var imageToEdit = document.getElementById('myCanvas');
    var maskedImage = document.getElementById('maskedImage');

    if (imageToEdit.children.length > 0) {
        var selectedImage = imageToEdit.children[0];
        var selectedMask = maskedImage.children[0];
        var photoId = selectedImage.getAttribute('data-photo-id');
        var maskUrl = selectedMask.getAttribute('src')

        var formData = new FormData(document.getElementById('myForm'));
        var photoModel = selectedImage.getAttribute('data-photo-model');

        formData.append('photo_id', photoId);
        formData.append('photo_model', photoModel);
        formData.append('maskUrl', maskUrl)


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

var selectedImage = null;



function moveImageToEdit(imgElement, sourceContainerId, targetContainerId) {
    var sourceContainer = document.getElementById(sourceContainerId);
    var targetContainer = document.getElementById(targetContainerId);
    var changedImgContainer = document.getElementById('changed_img');
    var saveButton = document.getElementById('saveButton');
    var resetButton = document.getElementById('resetButton');
    var instructionDiv = document.getElementById('instructionDiv');
    var maskedImageDiv = document.getElementById('maskedImage');

    var middleOptionsButton = document.getElementById('middleOptionsButton');

    saveButton.style.display = 'block';
    resetButton.style.display = 'block';
    instructionDiv.innerHTML = 'Start drawing, then press button to create mask';

    if (targetContainer.children.length > 0)  return;

    function resetImage() {
        maskedImageDiv.innerHTML = '';

        changedImgContainer.innerHTML = '';
        sourceContainer.appendChild(imgElement);
        imgElement.style.maxHeight = '100px';
        imgElement.onclick = function() {
            moveImageToEdit(this, sourceContainerId, targetContainerId);
        };
        selectedImage = null;
        instructionDiv.innerHTML = 'Click image from below to add to edit';
        saveButton.style.display = 'none';
        resetButton.style.display = 'none';

        middleOptionsButton.style.display = 'none';
        clearCanvas();
    }

    sourceContainer.removeChild(imgElement);
    imgElement.style.maxHeight = '200px';

    imgElement.onclick = resetImage;

    targetContainer.appendChild(imgElement);
    selectedImage = imgElement;
    createCanvas();
    if (resetButton) resetButton.onclick = resetImage;
}

var saveButton = document.getElementById('saveButton');
if (saveButton) saveButton.onclick = saveImage;

function clearCanvas() {
    context.clearRect(0, 0, canvas.width, canvas.height);
}


var originalImage = selectedImage || document.getElementById('originalImage');
var canvas = document.getElementById('myCanvas');
var context = canvas.getContext('2d');

function createCanvas(){
    originalImage = selectedImage || document.getElementById('originalImage');
    canvas = document.getElementById('myCanvas');
    context = canvas.getContext('2d');
    var maxHeight = 280;

    var aspectRatio = originalImage.width / originalImage.height;

    if (originalImage.height > maxHeight) {
        canvas.height = maxHeight;
        canvas.width = maxHeight * aspectRatio;
    } else {
        canvas.width = originalImage.width;
        canvas.height = originalImage.height;
    }
    context.drawImage(originalImage, 0, 0, canvas.width, canvas.height);

    var isDrawing = false;

    function startDrawing(e) {
        isDrawing = true;
        draw(e);
    }

    function stopDrawing() {
        isDrawing = false;
        context.beginPath();
    }

    function draw(e) {
        if (!isDrawing) return;

        context.lineWidth = 50;
        context.lineCap = 'round';
        context.strokeStyle = '#b803ff';

        var rect = canvas.getBoundingClientRect();
        var x = e.clientX - rect.left;
        var y = e.clientY - rect.top;

        context.lineTo(x, y);
        context.stroke();
        context.beginPath();
        context.moveTo(x, y);
    }

    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
}

function saveImage() {
    var middleOptionsButton = document.getElementById('middleOptionsButton');
    middleOptionsButton.style.display = 'block';


    var imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    var tolerance = 5;

    for (var i = 0; i < imageData.data.length; i += 4) {
        var red = imageData.data[i];
        var green = imageData.data[i + 1];
        var blue = imageData.data[i + 2];

        var isPurple = Math.abs(red - 184) <= tolerance &&
            Math.abs(green - 3) <= tolerance &&
            Math.abs(blue - 255) <= tolerance;

        if (isPurple) {
            imageData.data[i] = 255; 
            imageData.data[i + 1] = 255; 
            imageData.data[i + 2] = 255;
        } else {
            imageData.data[i] = 0;
            imageData.data[i + 1] = 0;
            imageData.data[i + 2] = 0;
        }
    }

    context.putImageData(imageData, 0, 0);

    var editedImage = canvas.toDataURL('image/png');
    var maskedImageDiv = document.getElementById('maskedImage');
    maskedImageDiv.innerHTML = '<img src="' + editedImage + '" style="max-height: 500px;">';

    context.drawImage(originalImage, 0, 0, canvas.width, canvas.height);
}




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

