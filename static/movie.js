var btn = document.getElementById('button');
var voc = document.getElementById('vocabulary');
var inp = document.getElementById('word');
var btn_search = document.getElementById('search-btn');
// var btn_flashcard = document.getElementById('btn-flashcard');

btn.addEventListener('click', sendRequest);

btn_search.addEventListener('click', add_to_vocab);
// btn_flashcard.addEventListener('click', add_to_flashcards)

function sendRequest() {
    var xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function () {
        if (this.readyState === this.DONE) {
            var response = JSON.parse(this.responseText)
            voc.innerHTML = '<th>Word</th>\n' +
                '            <th>Definition</th>\n' +
                '            ';
            var wordsLen = response.length;
            if (wordsLen != 0) {
                var i = 0;
                response.forEach(function (word) {
                    if (word.shortdef != '' && word.shortdef != undefined) {
                        voc.innerHTML += '<tr><td>' + inp.value + '</td><td>' + word.shortdef + '</td></tr>';
                        i = i + 1;
                    }
                });
                if (i == 0) {
                    voc.innerHTML += '<tr><td>0 definitions found</td></tr>';
                }
            } else {
                voc.innerHTML += '<tr><td>0 definitions found</td></tr>';
            }
        }
    }

    xhr.open('GET', 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/' + inp.value + '?key=27f7ff07-147b-4a26-a4ea-f97c5d5f0198');
    xhr.send('');
}

function add_to_vocab() {
    event.preventDefault();

    var formData = {
        'word': $('input[name=word]').val(), //for get email
        'desc': $('input[name=desc]').val(), //for get email
        'id': $('input[name=id]').val() //for get email
    };
    console.log(formData);

    $.ajax({
        url: "/add_to_dict",
        type: "post",
        data: formData,
        success: function (d) {
            location.reload();
        }
    });
}

function add_to_flashcards(front, back) {
    event.preventDefault();

    var formData = {
        'front': front, //for get email
        'back': back, //for get email
    };
    console.log(formData);

    $.ajax({
        url: "/add_to_flashcards",
        type: "post",
        data: formData,
        success: function (d) {
        }
    });
}