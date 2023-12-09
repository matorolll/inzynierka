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
            document.getElementById('changed_img').innerHTML = '<img src="' + data.changed_image_url + '" alt="changed image" style="max-height: 200px">';
            var ganImage = document.createElement('img');
            ganImage.src = data.changed_image_url;
            ganImage.alt = 'changed image';
            ganImage.style = 'max-height: 100px';
            document.getElementById('gan_image_from_base').appendChild(ganImage);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    } else {
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