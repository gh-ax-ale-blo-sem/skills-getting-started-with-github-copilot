document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Helper function to sanitize text content
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Helper function to show message
  function showMessage(text, type = 'info') {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");
    
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  // Function to create participant list item
  function createParticipantElement(participant, activityName) {
    const li = document.createElement('li');
    
    const emailSpan = document.createElement('span');
    emailSpan.className = 'participant-email';
    emailSpan.textContent = participant;
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-btn';
    deleteBtn.dataset.activity = activityName;
    deleteBtn.dataset.email = participant;
    deleteBtn.title = 'Unregister participant';
    deleteBtn.textContent = '🗑️';
    deleteBtn.addEventListener('click', handleDelete);
    
    li.appendChild(emailSpan);
    li.appendChild(deleteBtn);
    
    return li;
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const activities = await response.json();

      // Clear loading message and activities list
      activitiesList.innerHTML = "";
      
      // Clear and reset activity select (keeping the default option)
      const defaultOption = activitySelect.querySelector('option[value=""]');
      activitySelect.innerHTML = '';
      if (defaultOption) {
        activitySelect.appendChild(defaultOption);
      }

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const isFull = spotsLeft === 0;

        // Create title
        const title = document.createElement('h4');
        title.textContent = name;
        activityCard.appendChild(title);

        // Create description
        const description = document.createElement('p');
        description.textContent = details.description;
        activityCard.appendChild(description);

        // Create schedule
        const schedule = document.createElement('p');
        const scheduleStrong = document.createElement('strong');
        scheduleStrong.textContent = 'Schedule: ';
        schedule.appendChild(scheduleStrong);
        schedule.appendChild(document.createTextNode(details.schedule));
        activityCard.appendChild(schedule);

        // Create availability
        const availability = document.createElement('p');
        const availStrong = document.createElement('strong');
        availStrong.textContent = 'Availability: ';
        availability.appendChild(availStrong);
        availability.appendChild(document.createTextNode(
          isFull ? 'Full' : `${spotsLeft} spot${spotsLeft !== 1 ? 's' : ''} left`
        ));
        if (isFull) {
          availability.style.color = '#c62828';
          availability.style.fontWeight = 'bold';
        }
        activityCard.appendChild(availability);

        // Create participants section
        const participantsDiv = document.createElement('div');
        participantsDiv.className = 'participants';
        
        const participantsTitle = document.createElement('h5');
        participantsTitle.textContent = 'Participants';
        participantsDiv.appendChild(participantsTitle);

        if (details.participants.length > 0) {
          const ul = document.createElement('ul');
          details.participants.forEach(participant => {
            ul.appendChild(createParticipantElement(participant, name));
          });
          participantsDiv.appendChild(ul);
        } else {
          const noParticipants = document.createElement('p');
          noParticipants.className = 'no-participants';
          noParticipants.textContent = 'No participants yet';
          participantsDiv.appendChild(noParticipants);
        }
        
        activityCard.appendChild(participantsDiv);
        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        if (isFull) {
          option.disabled = true;
          option.textContent = `${name} (Full)`;
        }
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p class='error'>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle delete participant
  async function handleDelete(event) {
    const button = event.currentTarget;
    const activity = button.dataset.activity;
    const email = button.dataset.email;

    if (!confirm(`Are you sure you want to unregister ${email} from ${activity}?`)) {
      return;
    }

    // Disable button during request
    button.disabled = true;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        await fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
        button.disabled = false;
      }
    } catch (error) {
      showMessage("Failed to unregister participant. Please try again.", "error");
      button.disabled = false;
      console.error("Error unregistering participant:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const emailInput = document.getElementById("email");
    const activityInput = document.getElementById("activity");
    const submitButton = signupForm.querySelector('button[type="submit"]');
    
    const email = emailInput.value.trim();
    const activity = activityInput.value;

    if (!activity) {
      showMessage("Please select an activity", "error");
      return;
    }

    // Disable form during submission
    submitButton.disabled = true;
    emailInput.disabled = true;
    activityInput.disabled = true;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        await fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    } finally {
      // Re-enable form
      submitButton.disabled = false;
      emailInput.disabled = false;
      activityInput.disabled = false;
    }
  });

  // Initialize app
  fetchActivities();
});
