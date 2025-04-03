// Main application initialization
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Feather icons
    feather.replace();

    // Initialize event cards
    const eventsContainer = document.querySelector('.events-container');
    if (eventsContainer) {
        eventData.featuredEvents.forEach(event => {
            const eventCard = new EventCard(event);
            eventsContainer.innerHTML += eventCard.render();
        });
    }

    // Initialize category cards
    const categoriesContainer = document.querySelector('.categories-container');
    if (categoriesContainer) {
        eventData.categories.forEach(category => {
            const categoryCard = new CategoryCard(category);
            categoriesContainer.innerHTML += categoryCard.render();
        });
    }

    // Re-render Feather icons after adding new content
    feather.replace();
}); 