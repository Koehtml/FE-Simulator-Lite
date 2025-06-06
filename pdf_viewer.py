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
        self.search_results = []  # Store search results
        self.current_search_index = -1  # Current position in search results
        
        # Track dragging state
        self.is_dragging = False
        self.last_x = 0
        self.last_y = 0
        
        # Configure grid weights
        self.grid_rowconfigure(2, weight=1)  # Changed from 1 to 2 to accommodate search bar
        self.grid_columnconfigure(0, weight=1)
        
        # Create toolbar
        self.create_toolbar()
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Create search bar (initially hidden)
        self.search_frame = ttk.Frame(self)
        self.search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        self.search_frame.grid_remove()  # Hide initially
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Search navigation buttons
        ttk.Button(self.search_frame, text="↑", width=3, command=self.prev_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.search_frame, text="↓", width=3, command=self.next_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.search_frame, text="✕", width=3, command=self.hide_search).pack(side=tk.LEFT, padx=2)
        
        # Create canvas for PDF display
        self.canvas = tk.Canvas(self, bg='white', cursor="arrow")
        self.canvas.grid(row=2, column=0, sticky="nsew", padx=(5,0), pady=5)
        
        # Create scrollbars
        self.v_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.grid(row=2, column=1, sticky="ns", pady=5)
        
        self.h_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.grid(row=3, column=0, sticky="ew", padx=5)
        
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Bind events
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Button-3>', self.on_right_click)
        
        # Mouse wheel for page navigation
        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)
        # Ctrl + Mouse wheel for zooming
        self.canvas.bind_all('<Control-MouseWheel>', self.on_ctrl_mousewheel)
        
        # Add drag events for left mouse button
        self.canvas.bind('<ButtonPress-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.drag)
        self.canvas.bind('<ButtonRelease-1>', self.stop_drag)
        
        # Bind Ctrl+F for search
        self.bind_all('<Control-f>', self.show_search)
        self.bind_all('<Control-F>', self.show_search)
        
        # Bind Enter key in search entry
        self.search_entry.bind('<Return>', self.perform_search)
        
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
        """Handle canvas click event for PDF loading"""
        if not self.pdf_document:
            self.browse_pdf()

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
        """Handle mouse wheel for page navigation"""
        if not self.pdf_document:
            return
            
        if event.delta > 0:  # Scroll up
            self.prev_page()
        else:  # Scroll down
            self.next_page()

    def on_ctrl_mousewheel(self, event):
        """Handle Ctrl + mouse wheel for zooming"""
        if not self.pdf_document:
            return
            
        # Calculate the current page dimensions
        page = self.pdf_document[self.current_page]
        page_width = page.rect.width
        page_height = page.rect.height
        
        # Calculate the canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Calculate the minimum zoom level needed to fit the page
        min_zoom_x = canvas_width / page_width
        min_zoom_y = canvas_height / page_height
        min_zoom = min(min_zoom_x, min_zoom_y)
            
        if event.delta > 0:  # Zoom in
            if self.zoom_level < 3.0:  # Limit maximum zoom
                self.zoom_level += 0.1
                self.update_page()
        else:  # Zoom out
            if self.zoom_level > min_zoom:  # Limit minimum zoom to fit page
                self.zoom_level -= 0.1
                self.update_page()

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

    def show_search(self, event=None):
        """Show the search bar and focus the search entry"""
        self.search_frame.grid()
        self.search_entry.focus_set()
        
    def hide_search(self):
        """Hide the search bar and clear search results"""
        self.search_frame.grid_remove()
        self.search_var.set("")
        self.search_results = []
        self.current_search_index = -1
        self.display_page()  # Refresh the display to remove highlights
        
    def perform_search(self, event=None):
        """Perform search in the PDF document"""
        if not self.pdf_document:
            return
            
        search_text = self.search_var.get().strip()
        if not search_text:
            return
            
        # Clear previous search results
        self.search_results = []
        self.current_search_index = -1
        
        # Search through all pages
        for page_num in range(self.total_pages):
            page = self.pdf_document[page_num]
            text_instances = page.search_for(search_text)
            
            for inst in text_instances:
                self.search_results.append((page_num, inst))
        
        if self.search_results:
            self.current_search_index = 0
            self.jump_to_search_result()
        else:
            messagebox.showinfo("Search", "No matches found.")
            
    def jump_to_search_result(self):
        """Jump to the current search result"""
        if not self.search_results or self.current_search_index < 0:
            return
            
        page_num, rect = self.search_results[self.current_search_index]
        
        # Jump to the page
        if page_num != self.current_page:
            self.current_page = page_num
            self.display_page()
        
        # Highlight the search result
        self.highlight_search_result(rect)
        
    def highlight_search_result(self, rect):
        """Highlight the current search result on the page"""
        # Convert the rectangle coordinates to canvas coordinates
        zoom = 2 * self.zoom_level
        x0 = rect.x0 * zoom
        y0 = rect.y0 * zoom
        x1 = rect.x1 * zoom
        y1 = rect.y1 * zoom
        
        # Create a yellow highlight rectangle with less transparency
        self.canvas.create_rectangle(x0, y0, x1, y1, 
                                   fill='#FFFF00',  # Yellow
                                   stipple='gray25',  # Less transparent
                                   tags='search_highlight')
        
        # Ensure the highlight is visible
        self.canvas.see('search_highlight')
        
    def next_search(self):
        """Move to the next search result"""
        if not self.search_results:
            return
            
        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        self.jump_to_search_result()
        
    def prev_search(self):
        """Move to the previous search result"""
        if not self.search_results:
            return
            
        self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
        self.jump_to_search_result()

    def start_drag(self, event):
        """Start dragging the canvas"""
        if not self.pdf_document:
            # If no PDF is loaded, open file dialog
            self.browse_pdf()
            return
            
        # If PDF is loaded, start dragging
        self.is_dragging = True
        self.last_x = event.x
        self.last_y = event.y
        self.canvas.config(cursor="fleur")  # Change cursor to indicate dragging

    def drag(self, event):
        """Handle canvas dragging"""
        if self.is_dragging:
            # Calculate the distance moved
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            
            # Scale down the movement for smoother panning
            scale_factor = 0.3  # Moderate sensitivity reduction
            dx = int(dx * scale_factor)
            dy = int(dy * scale_factor)
            
            # Move the canvas
            self.canvas.xview_scroll(-dx, "units")
            self.canvas.yview_scroll(-dy, "units")
            
            # Update last position
            self.last_x = event.x
            self.last_y = event.y

    def stop_drag(self, event):
        """Stop dragging the canvas"""
        self.is_dragging = False
        self.canvas.config(cursor="arrow")

    def zoom_in_at_position(self, x, y):
        """Zoom in at the specified position"""
        if self.zoom_level < 3.0:  # Limit maximum zoom
            self.zoom_level += 0.5
            self.update_page()

    def update_page(self):
        self.display_page() 