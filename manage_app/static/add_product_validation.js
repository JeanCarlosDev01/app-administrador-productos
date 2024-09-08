const imagesForm = document.getElementById('form-images')

function addUrl() {
    let div = document.createElement('div')
    div.classList.add('mb-3')
    div.innerHTML = `<button style="border: none;" class="p-0 m-1" onclick="deleteInput(this)"><i class="bi bi-x-square text-danger"></i></button>
                        <label for="inputUrl" class="form-label">Imagen</label>
                        <input type="url" class="form-control" name="image" id="inputUrl" placeholder="https://imagen1.jpg (png, webp ...)">`
    imagesForm.appendChild(div)
}

function getUrls() {
    let inputsList = imagesForm.querySelectorAll('#inputUrl')
    let urls = ''
    inputsList.forEach((input) => {
        if (input.value != '') {
            urls += `${input.value},`
        }
    })
    let urlsInput = document.getElementById('url-text')
    urlsInput.value = urls
    if (urlsInput.value != '') {
        document.getElementById('images-check').hidden = false
        return
    }
    document.getElementById('images-check').hidden = true
}

function deleteInput(element) {
    element.parentElement.remove()
    getUrls()
}

imagesForm.addEventListener('submit', (event) => {
    event.preventDefault()
    if (imagesForm.checkValidity()) {
        getUrls()
    }

})
