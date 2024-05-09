import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image
Image.MAX_IMAGE_PIXELS = None # Disable DecompressionBombError

def create_legend(community_label_colors: list[tuple[str,str]], filename: str ='./data/legend.png') -> None:

    fig, ax = plt.subplots(figsize=(10, 5))  # Adjust figure size as needed
    fig.patch.set_alpha(0.0)  # Transparent background
    ax.axis('off')
    
    
    patches = [mpatches.Patch(color=color, label=label) for label, color in community_labels_colors]
    
    # Adjust fontsize for clarity, frameon=False removes the legend background
    legend = plt.legend(handles=patches, loc='upper left', fontsize=50, frameon=False)
    
    for text in legend.get_texts():
        text.set_color("white")
    
    plt.savefig(filename, bbox_inches='tight', transparent=True, dpi=300)
    plt.close()







def merge_legend_with_plot(plot_image_path: str, legend_image_path: str, output_path: str) -> None:
    
    plot_img = Image.open(plot_image_path)
    legend_img = Image.open(legend_image_path)
    
    # Calculate the position for the legend: top-right corner
    plot_width, plot_height = plot_img.size
    legend_width, legend_height = legend_img.size
    x_position = plot_width - legend_width - 50  # Adjust margins as needed
    y_position = 50  # Margin from the top
    
    transparent_overlay = Image.new("RGBA", plot_img.size, (0, 0, 0, 0))
    transparent_overlay.paste(legend_img, (x_position, y_position), legend_img)
    combined = Image.alpha_composite(plot_img.convert("RGBA"), transparent_overlay)
    combined.save(output_path)


def main():
    community_labels_colors = [
        ("Sensory and Cognitive Processes", "#FF5733"),  # Red
        ("Mental Health and Clinical Psychology", "#33FF57"),  # Lime
        ("Educational Psychology and Development", "#3357FF"),  # Blue
        ("Neuroscience and Neurology", "#F933FF"),  # Magenta
        ("Social Psychology and Society", "#33FFF9"),  # Cyan
        ("Language, Cognition, and Neuroscience", "#F9FF33"),  # Yellow
        ("Education and Developmental Psychology", "#FF8333"),  # Orange
        ("Applied Psychology and Organizational Behavior", "#8333FF"),  # Purple
        ("Cognitive Processes and Experimental Psychology", "#33FF83"),  # Green
        ("Integrative Psychology, Arts and Humanities", "#FF3333")   # Bright Red
    ]

    create_legend(community_labels_colors)

    merge_legend_with_plot('./data/graph.png', './data/legend.png', './data/annotated_graph.png')

if __name__ == '__main__':
    main()