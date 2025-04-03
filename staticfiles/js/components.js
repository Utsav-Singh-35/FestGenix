// UI Components
class EventCard {
    constructor(event) {
        this.event = event;
    }

    render() {
        return `
            <div class="event-card">
                <h3>${this.event.title}</h3>
                <p>Date: ${this.event.date}</p>
                <p>Location: ${this.event.location}</p>
                <p>Category: ${this.event.category}</p>
            </div>
        `;
    }
}

class CategoryCard {
    constructor(category) {
        this.category = category;
    }

    render() {
        return `
            <div class="category-card">
                <i data-feather="${this.category.icon}"></i>
                <h3>${this.category.name}</h3>
                <p>${this.category.description}</p>
            </div>
        `;
    }
} 