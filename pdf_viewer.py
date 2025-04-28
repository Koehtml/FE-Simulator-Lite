import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import os
import sys
import traceback
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import threading

class PDFViewer(ttk.Frame):
    def __init__(self, parent, pdf_path=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.current_page = 0
        self.images = []
        self.photo_images = []
        self.total_pages = 0
        self.zoom_level = 1.0
        self.pdf_document = None
        
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create toolbar
        self.create_toolbar()
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Create canvas for PDF display
        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=(5,0), pady=5)
        
        # Create scrollbars
        self.v_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.grid(row=1, column=1, sticky="ns", pady=5)
        
        self.h_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.grid(row=2, column=0, sticky="ew", padx=5)
        
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Bind events
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.canvas.bind('<Button-1>', self.on_canvas_click)  # Left click for both zoom and PDF loading
        self.canvas.bind('<Button-3>', self.on_right_click)  # Right click for zoom out
        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)  # Windows mousewheel
        
        # If no PDF is provided, show a message to click to load a PDF
        if not pdf_path:
            self.show_load_pdf_message()
        else:
            # Load PDF in a separate thread
            self.load_thread = threading.Thread(target=self.load_pdf)
            self.load_thread.daemon = True
            self.load_thread.start()

    def show_load_pdf_message(self):
        """Display a message prompting the user to click to load a PDF"""
        self.canvas.delete("all")
        self.canvas.create_text(
            self.canvas.winfo_width() // 2,
            self.canvas.winfo_height() // 2,
            text="Click here to load a PDF file",
            font=("Arial", 14),
            fill="gray"
        )
        self.page_label.config(text="No PDF loaded")
    
    def on_canvas_click(self, event):
        """Handle canvas click event for both zoom and PDF loading"""
        if not self.pdf_document:
            self.browse_pdf()
        else:
            self.zoom_in()
    
    def browse_pdf(self):
        """Open a file dialog to browse for a PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.pdf_path = file_path
            # Load PDF in a separate thread
            self.load_thread = threading.Thread(target=self.load_pdf)
            self.load_thread.daemon = True
            self.load_thread.start()
        
    def create_toolbar(self):
        self.toolbar = ttk.Frame(self)
        
        # Navigation buttons
        ttk.Button(self.toolbar, text="◀", command=self.prev_page, width=3).pack(side=tk.LEFT, padx=2)
        self.page_label = ttk.Label(self.toolbar, text="Page: 0/0")
        self.page_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.toolbar, text="▶", command=self.next_page, width=3).pack(side=tk.LEFT, padx=2)
        
        # Zoom buttons
        ttk.Button(self.toolbar, text="+", command=self.zoom_in, width=3).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.toolbar, text="-", command=self.zoom_out, width=3).pack(side=tk.LEFT, padx=2)
        
        # Add a button to browse for a new PDF
        ttk.Button(self.toolbar, text="📂", command=self.browse_pdf, width=3).pack(side=tk.LEFT, padx=5)
        
    def load_pdf(self):
        try:
            # Check if running as a frozen executable
            if getattr(sys, 'frozen', False):
                # Running in a bundle
                bundle_dir = os.path.dirname(sys.executable)
                # Try to find the PDF in the bundle directory
                bundle_pdf_path = os.path.join(bundle_dir, os.path.basename(self.pdf_path))
                if os.path.exists(bundle_pdf_path):
                    self.pdf_path = bundle_pdf_path
                    print(f"Using PDF from bundle: {self.pdf_path}")
            
            # Check if PDF file exists
            if not os.path.exists(self.pdf_path):
                error_msg = f"PDF file not found: {self.pdf_path}"
                print(error_msg)
                print(f"Current directory: {os.getcwd()}")
                print(f"__file__: {__file__}")
                print(f"sys.executable: {sys.executable}")
                print(f"sys.path: {sys.path}")
                self.after(0, lambda: messagebox.showerror("Error", error_msg))
                return
                
            print(f"Loading PDF: {self.pdf_path}")
            
            # Open the PDF document
            self.pdf_document = fitz.open(self.pdf_path)
            self.total_pages = len(self.pdf_document)
            print(f"Successfully loaded {self.total_pages} pages")
            
            # Display the first page
            self.after(0, self.display_page)
            
        except Exception as e:
            error_msg = f"Failed to load PDF: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            print(error_msg)
            self.after(0, lambda: messagebox.showerror("Error", error_msg))

    def display_page(self):
        if not self.pdf_document:
            print("No PDF document loaded")
            return
            
        try:
            print(f"Displaying page {self.current_page + 1}/{self.total_pages}")
            
            # Get the page
            page = self.pdf_document[self.current_page]
            
            # Get page dimensions
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            # Get frame dimensions
            frame_width = self.canvas.winfo_width()
            frame_height = self.canvas.winfo_height()
            
            # Calculate zoom to fit if this is the first page
            if self.current_page == 0 and frame_width > 1 and frame_height > 1:
                # Calculate zoom factors for both dimensions
                width_zoom = (frame_width - 20) / page_width  # -20 for padding
                height_zoom = (frame_height - 20) / page_height  # -20 for padding
                
                # Use the smaller zoom factor to ensure the page fits
                self.zoom_level = min(width_zoom, height_zoom) / 2  # Divide by 2 because base zoom is 2
            
            # Render the page to a pixmap
            zoom = 2 * self.zoom_level  # Base zoom is 2 for better quality
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Clear canvas
            self.canvas.delete("all")
            
            # Display the image
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            
            # Keep a reference to prevent garbage collection
            self.current_photo = photo
            
            # Update page label
            self.page_label.config(text=f"Page: {self.current_page + 1} of {self.total_pages}")
            
            # Update scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        except Exception as e:
            error_msg = f"Failed to display page: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            print(error_msg)
            self.after(0, lambda: messagebox.showerror("Error", error_msg))

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()
            
    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_page()

    def on_mousewheel(self, event):
        # Windows mousewheel
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_left_click(self, event):
        self.zoom_in()
        
    def on_right_click(self, event):
        self.zoom_out()

    def zoom_in(self):
        self.zoom_level *= 1.2
        self.display_page()
        
    def zoom_out(self):
        self.zoom_level /= 1.2
        self.display_page()
        
    def on_canvas_configure(self, event):
        # Update scroll region when canvas is resized
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # If this is the first resize and we have a page loaded, fit it to the frame
        if hasattr(self, 'current_photo') and self.current_page == 0:
            self.display_page()  # This will recalculate the zoom level 

    def jump_to_page(self, page_number):
        """Jump to a specific page number (0-based)"""
        if 0 <= page_number < self.total_pages:
            self.current_page = page_number
            self.display_page() 