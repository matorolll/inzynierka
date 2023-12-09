function checkAndSubmit() {
    var formData = new FormData(document.getElementById('myForm'));
        
    fetch(document.getElementById('myForm').action, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('changed_img').innerHTML = '<img src="' + data.changed_image_url + '" alt="Changed Image" style="max-height: 200px">';
        var texttoimage = document.createElement('img');
        texttoimage.src = data.changed_image_url;
        texttoimage.alt = 'changed image';
        texttoimage.style = 'max-height: 100px';
        document.getElementById('texttoimage_image_from_base').appendChild(texttoimage);
    })
    .catch(error => { console.error('Error:', error)});
}

function generateRandomSeed() {
    var randomSeed = Math.floor(Math.random() * 1000000000) + 1;
    document.getElementById("seed_input").value = randomSeed;
}

var guidanceSlider = document.getElementById("guidance_scale_input");
var guidanceOutput = document.querySelector("output[for=guidance_scale_input]");

var stepsSlider = document.getElementById("steps_input");
var stepsOutput = document.querySelector("output[for=steps_input]");

guidanceSlider.addEventListener("input", function() {
    guidanceOutput.textContent = guidanceSlider.value;
});

guidanceSlider.addEventListener("change", function() {
    guidanceOutput.textContent = guidanceSlider.value;
});

stepsSlider.addEventListener("input", function() {
    stepsOutput.textContent = stepsSlider.value;
});

stepsSlider.addEventListener("change", function() {
    stepsOutput.textContent = stepsSlider.value;
});