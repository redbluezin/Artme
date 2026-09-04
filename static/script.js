/* =========================
   PESQUISA
========================= */

const form =
    document.getElementById(
        "searchForm"
    );


const input =
    document.getElementById(
        "searchInput"
    );


if (form && input) {

    form.addEventListener(
        "submit",
        function(event) {

            event.preventDefault();

            pesquisar();

        }
    );


    input.addEventListener(
        "input",
        pesquisar
    );

}


function pesquisar() {

    const texto =
        input.value
            .trim()
            .toLowerCase();


    const apps =
        document.querySelectorAll(
            ".searchable"
        );


    apps.forEach(
        function(app) {

            const nome =
                app.dataset.name || "";


            if (
                nome.includes(texto)
            ) {

                app.style.display =
                    "";

            }

            else {

                app.style.display =
                    "none";

            }

        }
    );

}


/* =========================
   CARROSSEL
   DRAG COM MOUSE
========================= */

const carousel =
    document.getElementById(
        "screenshots"
    );


if (carousel) {

    let isDown = false;

    let startX;

    let scrollLeft;


    carousel.addEventListener(
        "mousedown",
        function(event) {

            isDown = true;


            carousel.classList.add(
                "dragging"
            );


            startX =
                event.pageX -
                carousel.offsetLeft;


            scrollLeft =
                carousel.scrollLeft;

        }
    );


    carousel.addEventListener(
        "mouseleave",
        function() {

            isDown = false;

        }
    );


    carousel.addEventListener(
        "mouseup",
        function() {

            isDown = false;

        }
    );


    carousel.addEventListener(
        "mousemove",
        function(event) {

            if (!isDown) {

                return;

            }


            event.preventDefault();


            const x =
                event.pageX -
                carousel.offsetLeft;


            const walk =
                (x - startX) * 1.5;


            carousel.scrollLeft =
                scrollLeft - walk;

        }
    );

}