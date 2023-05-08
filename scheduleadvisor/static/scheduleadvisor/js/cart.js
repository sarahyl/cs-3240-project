//https://www.youtube.com/watch?v=woORrr3QNh8&list=PL-51WBLyFTg0omnamUjL1TCVov7yDTRng&index=3

var updateButtons = document.getElementsByClassName('update-cart')

for (var i = 0; i < updateButtons.length; i++){
    updateButtons[i].addEventListener('click', function(){
        var class_number = this.dataset.course
        var action = this.dataset.action
        console.log(class_number, action)
        if (action == "add_course"){
            addCourseToCart(class_number, action)
        }
        else{ //action == "delete_course"
            deleteCourseFromCart(class_number, action)
        }
            
    })
}

//sends the data to the add course to cart view
function addCourseToCart(class_number, action){
    console.log("function addToCart")
    var url = '/studentindex/addtocart'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'class_number': class_number, 'action':action})
    })

    .then((response) => {
        return response.json()
    })

    .then((data) => {
        console.log('data',data)
    })
}

function deleteCourseFromCart(class_number, action){
    console.log("function deleteCourseFromCart")
    var url = '/cart/deletefromcart'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'class_number': class_number, 'action':action})
    })

    .then((response) => {
        return response.json()
    })

    .then((data) => {
        console.log('data',data)
        location.reload()
    })
}