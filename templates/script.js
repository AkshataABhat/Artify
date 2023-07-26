
const fileInput = document.querySelector(".file-input"),
filterOptions = document.querySelectorAll(".filter button"),
filterName = document.querySelector(".filter-info .name"),
filterValue = document.querySelector(".filter-info .value"),
filterSlider = document.querySelector(".slider input"),
rotateOptions = document.querySelectorAll(".rotate button"),
previewImg = document.querySelector(".preview-img img"),
resetFilterBtn = document.querySelector(".reset-filter"),
chooseImgBtn = document.querySelector(".choose-img"),
saveImgBtn = document.querySelector(".save-img");

let brightness = "50", saturation = "100", inversion = "0", grayscale = "0" ;
let rotate = 0, flipHorizontal = 1, flipVertical = 1;

// ... Your existing JavaScript code ...

const loadImage = () => {
    let file = fileInput.files[0];
    if (!file) return;

    const imageUrl = URL.createObjectURL(file);

    // Load the image into the 'original' region
    const originalImg = document.querySelector(".original-img img");
    originalImg.src = imageUrl;

    // Load the image into the 'preview' region
    const previewImg = document.querySelector(".preview-img img");
    previewImg.src = imageUrl;
    previewImg.style.filter = 'none';


    // Reset filters and enable the container
    resetFilterBtn.click();
    document.querySelector(".container").classList.remove("disable");


    // Send the image to the server for processing
    const formData = new FormData();
    formData.append('file', file);

    fetch('/process_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Update the 'preview' region with the processed image
        previewImg.src = 'data:image/jpeg;base64,' + data.encoded_image;

    })
    .catch(error => {
        console.error('Error:', error);
    });
};


const applyFilter = () => {
    previewImg.style.transform = `rotate(${rotate}deg) scale(${flipHorizontal}, ${flipVertical})`;
    previewImg.style.filter = `brightness(${brightness}%) saturate(${saturation}%) invert(${inversion}%) grayscale(${grayscale}%)`;


    // Make a POST request to the Flask server to apply the filters
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    if (filterName.innerText === "Brightness") {
        formData.append('filter', 'brightness');
        formData.append('value', parseInt(brightness)); // Parse brightness value as an integer
    } else if (filterName.innerText === "Saturation") {
        formData.append('filter', 'saturation');
        formData.append('value', parseInt(saturation)); // Parse saturation value as an integer
    } else if (filterName.innerText === "Inversion") {
        formData.append('filter', 'invert');
        formData.append('value', parseInt(inversion)); // Parse inversion value as an integer
    } else if (filterName.innerText === "Grayscale") {
        formData.append('filter', 'grayscale');
        formData.append('value', parseInt(grayscale)); // Parse grayscale value as an integer
     // Parse blur value as an integer
    } else {
        // If no filter is specified or the filter is not recognized, return the original image
        processed_image = image_array;
    }

    fetch('/process_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Update the 'preview' region with the processed image
        previewImg.src = 'data:image/jpeg;base64,' + data.encoded_image;
    })
    .catch(error => {
        console.error('Error:', error);
    });
};


filterOptions.forEach(option => {
    option.addEventListener("click", () => {
        document.querySelector(".active").classList.remove("active");
        option.classList.add("active");
        filterName.innerText = option.innerText;

        if(option.id === "brightness") {
            filterSlider.max = "100";
            filterSlider.value = brightness;
            filterValue.innerText = `${brightness}%`;
        } else if(option.id === "saturation") {
            filterSlider.max = "100";
            filterSlider.value = saturation;
            filterValue.innerText = `${saturation}%`
        } else if(option.id==="inversion"){
            filterSlider.max = "100";
            filterSlider.value = inversion;
            filterValue.innerText = `${inversion}%`;
        } else if(option.id==="grayscale"){
            filterSlider.max = "100";
            filterSlider.value = grayscale;
            filterValue.innerText = `${grayscale}%`;
        } else {
            // If an unrecognized filter option is clicked, reset filter settings to default
            filterSlider.max = "100";
            filterSlider.value = 50;
            filterValue.innerText = "50%";
        }
    });
});

const updateFilter = () => {
    filterValue.innerText = `${filterSlider.value}%`;
    const selectedFilter = document.querySelector(".filter .active");

    if(selectedFilter.id === "brightness") {
        brightness = filterSlider.value;
    } else if(selectedFilter.id === "saturation") {
        saturation = filterSlider.value;
    } else if(selectedFilter.id === "inversion") {
        inversion = filterSlider.value;
    } else if(selectedFilter.id === "grayscale"){
        grayscale = filterSlider.value;
    } else {
        // If no recognized filter is selected, you can set default values or do nothing
        // For example, you can set all filter values to 0 (no effect)
        brightness = "0";
        saturation = "0";
        inversion = "0";
        grayscale = "0";
    }
    applyFilter();
}

rotateOptions.forEach(option => {
    option.addEventListener("click", () => {
        if(option.id === "left") {
            rotate -= 90;
        } else if(option.id === "right") {
            rotate += 90;
        } else if(option.id === "horizontal") {
            flipHorizontal = flipHorizontal === 1 ? -1 : 1;
        } else {
            flipVertical = flipVertical === 1 ? -1 : 1;
        }
        applyFilter();
    });
});

const resetFilter = () => {
    previewImg.style.filter = 'none';

    brightness = "50"; saturation = "0"; inversion = "0"; grayscale = "0";
    rotate = 0; flipHorizontal = 1; flipVertical = 1;
    filterOptions[0].click();
    applyFilter();
}

const saveImage = () => {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    canvas.width = previewImg.naturalWidth;
    canvas.height = previewImg.naturalHeight;
    
    ctx.filter = `brightness(${brightness}%) saturate(${saturation}%) invert(${inversion}%) grayscale(${grayscale}%) `;
    ctx.translate(canvas.width / 2, canvas.height / 2);
    if(rotate !== 0) {
        ctx.rotate(rotate * Math.PI / 180);
    }
    ctx.scale(flipHorizontal, flipVertical);
    ctx.drawImage(previewImg, -canvas.width / 2, -canvas.height / 2, canvas.width, canvas.height);
    
    const link = document.createElement("a");
    link.download = "image.jpg";
    link.href = canvas.toDataURL();
    link.click();
}

filterSlider.addEventListener("input", updateFilter);
resetFilterBtn.addEventListener("click", resetFilter);
saveImgBtn.addEventListener("click", saveImage);
fileInput.addEventListener("change", loadImage);
chooseImgBtn.addEventListener("click", () => fileInput.click());