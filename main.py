import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

class AnnotationApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Annotation Tool")

        self.annotation_file = None
        self.image_dir = None
        self.gt_dir = None
        self.current_image_index = 0
        self.annotations = None
        self.images = None

        tk.Button(self.root, text="Select Annotation", command=self.load_annotation).pack(side=tk.LEFT)
        tk.Button(self.root, text="Select Image Directory", command=self.select_image_directory).pack(side=tk.LEFT)
        tk.Button(self.root, text="Select ground truth directory", command=self.select_gt_directory).pack(side=tk.LEFT)
        tk.Button(self.root, text="Start Annotating", command=self.start_annotating).pack(pady=20)

        self.root.mainloop()

    def load_annotation(self):
        self.annotation_file = filedialog.askopenfilename()
        with open(self.annotation_file, 'r') as f:
            data = json.load(f)
            self.annotations = data["annotations"]
            self.images = data["images"]

    def select_image_directory(self):
        self.image_dir = filedialog.askdirectory()

    def select_gt_directory(self):
        self.gt_dir = filedialog.askdirectory()

    def start_annotating(self):
        if not self.annotation_file:
            messagebox.showerror("Error", "Select the annotation file!")
            return

        if not self.image_dir:
            messagebox.showerror("Error", "Select the image directory!")
            return

        if not self.gt_dir:
            messagebox.showerror("Error", "Select the ground truth directory!")
            return

        self.annotate_image()

    def annotate_image(self):
        if self.current_image_index >= len(self.images):
            messagebox.showinfo("Info", "Annotation completed!")
            self.root.quit()
            return

        # Close any previous matplotlib plot
        plt.close()

        image_data = self.images[self.current_image_index]
        image_path = os.path.join(self.image_dir, image_data["file_name"])

        # Plot the image using matplotlib
        img = Image.open(image_path)
        plt.imshow(img)
        plt.title(image_data["file_name"])

        # Get the bounding boxes and draw them on the plot
        image_id = image_data["id"]
        bboxes = [ann for ann in self.annotations if ann["image_id"] == image_id]
        for idx, bbox in enumerate(bboxes):
            x, y, w, h = bbox["bbox"]
            plt.gca().add_patch(plt.Rectangle((x, y), w, h, fill=False, edgecolor='red', linewidth=2))
            plt.text(x, y, str(idx+1), color='red')
        
        # Display the plot
        plt.show(block=False)
        # Create a new window for annotation
        self.annotation_window = tk.Toplevel(self.root)
        self.annotation_window.title(image_data["file_name"])

        # Create input fields for ground truth
        self.gt_entries = []
        for idx in range(len(bboxes)):
            gt_label = tk.Label(self.annotation_window, text=f"Ground Truth {idx+1}:")
            gt_label.pack()

            gt_entry = tk.Entry(self.annotation_window)
            gt_entry.pack()
            self.gt_entries.append(gt_entry)

        tk.Button(self.annotation_window, text="Clear ground truth", command=self.clear_ground_truth).pack(pady=10)
        tk.Button(self.annotation_window, text="Finish and Go to Next Image", command=self.save_and_next).pack(pady=10)

    def clear_ground_truth(self):
        for entry in self.gt_entries:
            entry.delete(0, tk.END)

    def save_and_next(self):
        image_data = self.images[self.current_image_index]
        image_id = image_data["id"]
        bboxes = [ann for ann in self.annotations if ann["image_id"] == image_id]

        # Get the base name without extension for saving
        base_name = os.path.splitext(image_data['file_name'])[0]
        
        with open(os.path.join(self.gt_dir, f"{base_name}.txt"), 'w') as f:
            for idx, bbox in enumerate(bboxes):
                # Assuming bounding boxes are in the format [x, y, width, height]
                x, y, w, h = bbox["bbox"]
                gt_value = self.gt_entries[idx].get()
                f.write(f"{x},{y},{x+w},{y},{x+w},{y+h},{x},{y+h},\"{gt_value}\"\n")

        self.current_image_index += 1
        self.annotation_window.destroy()
        self.annotate_image()
if __name__ == "__main__":
    app = AnnotationApp()

