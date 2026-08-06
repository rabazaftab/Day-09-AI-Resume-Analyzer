const resume =
    document.getElementById("resume");

const jobDescription =
    document.getElementById(
        "jobDescription"
    );


const resumeCount =
    document.getElementById(
        "resumeCount"
    );


const jobCount =
    document.getElementById(
        "jobCount"
    );


const analyzeButton =
    document.getElementById(
        "analyzeButton"
    );


const results =
    document.getElementById(
        "results"
    );


const errorBox =
    document.getElementById(
        "error"
    );


resume.addEventListener(
    "input",
    () => {

        resumeCount.textContent =
            `${resume.value.length} / 10000`;

    }
);


jobDescription.addEventListener(
    "input",
    () => {

        jobCount.textContent =
            `${jobDescription.value.length} / 10000`;

    }
);


async function analyzeResume() {

    const resumeText =
        resume.value.trim();

    const jobText =
        jobDescription.value.trim();


    errorBox.textContent = "";

    results.classList.add(
        "hidden"
    );


    if (resumeText.length < 50) {

        errorBox.textContent =
            "Please enter a longer resume.";

        return;

    }


    if (jobText.length < 20) {

        errorBox.textContent =
            "Please enter a job description.";

        return;

    }


    analyzeButton.disabled = true;

    analyzeButton.textContent =
        "Analyzing...";


    try {

        const response =
            await fetch(
                "/analyze",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        resume:
                            resumeText,

                        job_description:
                            jobText

                    })

                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Analysis failed."
            );

        }


        document.getElementById(
            "score"
        ).textContent =
            `${data.match_score}%`;


        document.getElementById(
            "summary"
        ).textContent =
            data.summary;


        populateList(
            "strengths",
            data.strengths
        );


        populateList(
            "missingSkills",
            data.missing_skills
        );


        populateList(
            "suggestions",
            data.suggestions
        );


        results.classList.remove(
            "hidden"
        );


    }

    catch (error) {

        errorBox.textContent =
            error.message ||
            "Something went wrong.";

    }

    finally {

        analyzeButton.disabled =
            false;

        analyzeButton.textContent =
            "Analyze Resume";

    }

}


function populateList(
    elementId,
    items
) {

    const list =
        document.getElementById(
            elementId
        );


    list.innerHTML = "";


    if (
        !Array.isArray(items) ||
        items.length === 0
    ) {

        const li =
            document.createElement(
                "li"
            );

        li.textContent =
            "No items found.";

        list.appendChild(li);

        return;

    }


    items.forEach(
        item => {

            const li =
                document.createElement(
                    "li"
                );

            li.textContent =
                item;

            list.appendChild(li);

        }
    );

}