document.addEventListener("DOMContentLoaded", () => {

    const chips = document.querySelectorAll(".skill-chip");
    const input = document.getElementById("skillsInput");

    console.log("Input:", input);
    console.log("Chips:", chips.length);

    chips.forEach((chip) => {

        chip.addEventListener("click", () => {

            const skill = chip.textContent.trim();

            console.log("Clicked:", skill);

            let current = input.value
                .split(",")
                .map(item => item.trim())
                .filter(item => item);

            if (!current.includes(skill)) {

                current.push(skill);

                input.value = current.join(", ");

                chip.classList.add("active");

            } else {

                current = current.filter(
                    item => item !== skill
                );

                input.value = current.join(", ");

                chip.classList.remove("active");
            }

        });

    });

});

const form = document.getElementById("careerForm");
const loader = document.getElementById("loader");
const loaderText = document.getElementById("loaderText");

if(form){

    form.addEventListener("submit", () => {

        loader.style.display = "block";

        const messages = [
            "Analyzing Skills...",
            "Building Career Profile...",
            "Calculating Similarity...",
            "Finding Best Matches..."
        ];

        let index = 0;

        const interval = setInterval(() => {

            index++;

            if(index < messages.length){

                loaderText.innerText = messages[index];

            }

        }, 700);

    });

}
const particlesContainer =
document.getElementById("particles");

for(let i = 0; i < 50; i++){

    const particle =
    document.createElement("div");

    particle.classList.add("particle");

    particle.style.left =
    Math.random() * 100 + "%";

    particle.style.animationDuration =
    (5 + Math.random() * 10) + "s";

    particle.style.animationDelay =
    Math.random() * 5 + "s";

    particle.style.opacity =
    Math.random();

    particlesContainer.appendChild(
        particle
    );
}