lightbox.option({
    'resizeDuration': 200,
    'wrapAround': true
  })



  const getCSRFToken = () => {
      const cookieValue = document.cookie
          .split('; ')
          .find(row => row.startsWith('csrftoken='))
          .split('=')[1];
      return cookieValue;
  }
  
  
  const updateCounter = () => {
      const resultDiv = document.getElementById('selectedCounter');
      const selectedImages = document.querySelectorAll('.selected');
      resultDiv.innerHTML = `Selected: ${selectedImages.length}`;
  
  }
  
  
  const saveToDb = (images) =>{
      if (images instanceof NodeList) {
          const imageArray = Array.from(images);
          const photoIds = imageArray.map(image => image.getAttribute('alt'));
          const csrfToken = getCSRFToken();
          fetch('/update_photo_select_multiple/', {
          method: 'POST',
          headers: {
              'X-CSRFToken': csrfToken,
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ photoIds: photoIds })
      });
      }

      else if (images instanceof HTMLImageElement){
          const photoId = images.getAttribute('alt');
          const csrfToken = getCSRFToken();
          fetch(`/update_photo_select/${photoId}/`, {
              method: 'POST',
              headers: {
                  'X-CSRFToken': csrfToken,
                  'Content-Type': 'application/json'
              },
          });
      }

      
      updateCounter()
  }

  
  const GalleryEffects = () => {
    const images = document.querySelectorAll('img');
    const clearButton = document.getElementById('clearButton')

    clearButton.addEventListener('click', () =>{
      images.forEach((image) => {
          //image.classList.remove('selected');  border color

          //with checking
          //const heartIcon = image.nextElementSibling;
          //if (heartIcon && heartIcon.classList.contains('like-icon')) {
          //    heartIcon.classList.remove('clicked');
          //}
          image.nextElementSibling.classList.remove('clicked');
      });
      saveToDb(images);
    });

    images.forEach((image) => {
      const heartIcon = image.nextElementSibling;
      if (heartIcon && heartIcon.classList.contains('like-icon')) {
          heartIcon.addEventListener('contextmenu', () => {
              event.preventDefault();
              heartIcon.classList.toggle('clicked');
              saveToDb(image)
      })};

      if (image.getAttribute('data-selected')=== 'True') {
          heartIcon.classList.toggle('clicked');
      }
  
      image.addEventListener('contextmenu', () => {
          event.preventDefault();
          heartIcon.classList.toggle('clicked');
          saveToDb(image)
      });

      image.addEventListener('mouseover', () => {
          image.classList.add('onhover-effect');
      });
      
      image.addEventListener('mouseout', () => {
          image.classList.remove('onhover-effect');
      });
    });
    updateCounter(); //update onstart
  }
  window.addEventListener('load', GalleryEffects);