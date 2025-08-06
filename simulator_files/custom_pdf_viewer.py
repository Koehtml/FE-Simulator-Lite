import tkinter as tk
from tkinter import ttk, filedialog, messagebox
try:
    import fitz  # PyMuPDF
    print("Successfully imported fitz (PyMuPDF)")
except ImportError as e:
    print(f"Failed to import fitz: {e}")
    fitz = None
try:
    from PIL import Image, ImageTk
    print("Successfully imported PIL modules")
except ImportError as e:
    print(f"Failed to import PIL modules: {e}")
    Image = None
    ImageTk = None
import os
import sys
import threading
import traceback

class CustomPDFViewer(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pdf_document = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.current_photo = None
        
        # Search functionality
        self.search_results = []
        self.current_search_index = -1
        self.search_highlight_rects = []
        
        # Panning functionality
        self.is_panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.pan_start_scroll_x = 0
        self.pan_start_scroll_y = 0
        
        # Callback for when PDF is loaded
        self.pdf_loaded_callback = None
        
        # Debug logging
        print("CustomPDFViewer initialized")
        print(f"Running as frozen: {getattr(sys, 'frozen', False)}")
        if getattr(sys, 'frozen', False):
            print(f"Executable path: {sys.executable}")
            print(f"Bundle directory: {os.path.dirname(sys.executable)}")
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)  # Main content area
        self.grid_columnconfigure(0, weight=1)
        
        # Create widgets
        self.create_toolbar()
        self.create_search_bar()
        self.create_viewer()
        
        # Show initial message
        self.show_load_message()
        
    def set_pdf_loaded_callback(self, callback):
        """Set callback function to be called when PDF is loaded"""
        self.pdf_loaded_callback = callback
        
    def create_toolbar(self):
        """Create toolbar with navigation and controls"""
        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        
        # Navigation buttons
        self.prev_btn = ttk.Button(toolbar, text="◀", width=3, command=self.prev_page)
        self.prev_btn.pack(side=tk.LEFT, padx=2)
        
        self.page_label = ttk.Label(toolbar, text="No PDF loaded")
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        self.next_btn = ttk.Button(toolbar, text="▶", width=3, command=self.next_page)
        self.next_btn.pack(side=tk.LEFT, padx=2)
        
        # Zoom controls
        self.zoom_in_btn = ttk.Button(toolbar, text="+", width=3, command=self.zoom_in)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=5)
        
        self.zoom_out_btn = ttk.Button(toolbar, text="-", width=3, command=self.zoom_out)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=2)
        
        # Load PDF button
        ttk.Button(toolbar, text="📂", width=3, command=self.load_pdf).pack(side=tk.LEFT, padx=5)
        
    def create_search_bar(self):
        """Create search bar (initially hidden)"""
        self.search_frame = ttk.Frame(self)
        self.search_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=2)
        self.search_frame.grid_remove()  # Hide initially
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Search navigation buttons
        ttk.Button(self.search_frame, text="↑", width=3, command=self.prev_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.search_frame, text="↓", width=3, command=self.next_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.search_frame, text="✕", width=3, command=self.hide_search).pack(side=tk.LEFT, padx=2)
        
    def create_viewer(self):
        """Create the main PDF viewing area"""
        # Create frame for viewer
        viewer_frame = ttk.Frame(self)
        viewer_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        viewer_frame.grid_rowconfigure(0, weight=1)
        viewer_frame.grid_columnconfigure(0, weight=1)
        
        # Create canvas for PDF display
        self.canvas = tk.Canvas(
            viewer_frame,
            bg='white',
            highlightthickness=0,
            relief=tk.FLAT
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Create vertical scrollbar
        self.v_scrollbar = ttk.Scrollbar(
            viewer_frame,
            orient="vertical",
            command=self.canvas.yview
        )
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Create horizontal scrollbar
        self.h_scrollbar = ttk.Scrollbar(
            viewer_frame,
            orient="horizontal",
            command=self.canvas.xview
        )
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure canvas scrolling
        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        
        # Bind mouse wheel events for page navigation and zoom
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mousewheel)  # Linux scroll down
        
        # Bind Ctrl+scroll for zoom
        self.canvas.bind("<Control-MouseWheel>", self.on_ctrl_mousewheel)
        self.canvas.bind("<Control-Button-4>", self.on_ctrl_mousewheel)  # Linux
        self.canvas.bind("<Control-Button-5>", self.on_ctrl_mousewheel)  # Linux
        
        # Bind middle mouse button for panning
        self.canvas.bind("<Button-2>", self.start_pan)  # Middle mouse button
        self.canvas.bind("<B2-Motion>", self.pan)
        self.canvas.bind("<ButtonRelease-2>", self.stop_pan)
        
        # Bind click to load PDF
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Bind canvas resize
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind Ctrl+F for search
        self.bind_all("<Control-f>", self.show_search)
        self.bind_all("<Control-F>", self.show_search)
        
        # Bind Enter key in search entry
        self.search_entry.bind("<Return>", self.perform_search)
        
    def show_load_message(self):
        """Show message to load PDF"""
        self.canvas.delete("all")
        self.canvas.create_text(
            200, 150,
            text="Click here to load a PDF file",
            font=("Arial", 14),
            fill="gray"
        )
        
    def on_canvas_click(self, event):
        """Handle canvas click to load PDF"""
        if not self.pdf_document:
            self.load_pdf()
            
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        if self.pdf_document:
            self.display_current_page()
            
    def on_mousewheel(self, event):
        """Handle mouse wheel for page navigation"""
        if event.num == 5 or event.delta == -120:  # scroll down
            self.next_page()
        elif event.num == 4 or event.delta == 120:  # scroll up
            self.prev_page()
            
    def on_ctrl_mousewheel(self, event):
        """Handle Ctrl+mouse wheel for zoom"""
        if event.num == 5 or event.delta == -120:  # scroll down
            self.zoom_out()
        elif event.num == 4 or event.delta == 120:  # scroll up
            self.zoom_in()
            
    def start_pan(self, event):
        """Start panning with middle mouse button"""
        self.is_panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.pan_start_scroll_x = self.canvas.canvasx(0)
        self.pan_start_scroll_y = self.canvas.canvasy(0)
        self.canvas.config(cursor="fleur")  # Change cursor to indicate panning
        
    def pan(self, event):
        """Handle panning motion"""
        if not self.is_panning:
            return
            
        # Calculate the distance moved
        delta_x = self.pan_start_x - event.x
        delta_y = self.pan_start_y - event.y
        
        # Move the canvas view
        new_x = self.pan_start_scroll_x + delta_x
        new_y = self.pan_start_scroll_y + delta_y
        
        # Apply the pan with smooth movement
        self.canvas.xview_moveto(new_x / self.canvas.winfo_width())
        self.canvas.yview_moveto(new_y / self.canvas.winfo_height())
        
    def stop_pan(self, event):
        """Stop panning"""
        self.is_panning = False
        self.canvas.config(cursor="arrow")  # Restore normal cursor
        
    def show_search(self, event=None):
        """Show search bar"""
        self.search_frame.grid()
        self.search_entry.focus_set()
        
    def hide_search(self):
        """Hide search bar and clear highlights"""
        self.search_frame.grid_remove()
        self.clear_search_highlights()
        self.search_results = []
        self.current_search_index = -1
        
    def perform_search(self, event=None):
        """Perform search in the PDF across all pages"""
        if not self.pdf_document:
            return
            
        search_text = self.search_var.get().strip()
        if not search_text:
            return
            
        # Clear previous highlights
        self.clear_search_highlights()
        
        # Search across all pages
        all_results = []
        for page_num in range(self.total_pages):
            page = self.pdf_document[page_num]
            page_results = page.search_for(search_text)
            for rect in page_results:
                all_results.append((page_num, rect))
        
        if all_results:
            self.search_results = all_results
            self.current_search_index = 0
            self.jump_to_search_result()
        else:
            messagebox.showinfo("Search", f"No results found for '{search_text}' in the entire document")
            
    def jump_to_search_result(self):
        """Jump to the current search result"""
        if not self.search_results or self.current_search_index < 0:
            return
            
        # Get current result
        page_num, rect = self.search_results[self.current_search_index]
        
        # Navigate to the page if needed
        if page_num != self.current_page:
            self.current_page = page_num
            self.display_current_page()
            self.update_toolbar()
        
        # Highlight the result
        self.highlight_search_result()
        
    def highlight_search_result(self):
        """Highlight the current search result"""
        if not self.search_results or self.current_search_index < 0:
            return
            
        # Clear previous highlights
        self.clear_search_highlights()
        
        # Get current result
        page_num, rect = self.search_results[self.current_search_index]
        
        # Convert PDF coordinates to canvas coordinates
        canvas_rect = self.pdf_to_canvas_coords(rect)
        
        # Create highlight rectangle
        highlight = self.canvas.create_rectangle(
            canvas_rect[0], canvas_rect[1], canvas_rect[2], canvas_rect[3],
            outline="red", width=2, fill="yellow", stipple="gray50"
        )
        self.search_highlight_rects.append(highlight)
        
        # Scroll to highlight
        self.canvas.see(highlight)
        
        # Update search bar to show current result
        total_results = len(self.search_results)
        current_result = self.current_search_index + 1
        self.search_entry.config(style='SearchResult.TEntry')
        
    def clear_search_highlights(self):
        """Clear all search highlights"""
        for rect in self.search_highlight_rects:
            self.canvas.delete(rect)
        self.search_highlight_rects = []
        
    def pdf_to_canvas_coords(self, rect):
        """Convert PDF coordinates to canvas coordinates"""
        # This is a simplified conversion - you might need to adjust based on your zoom and positioning
        x0, y0, x1, y1 = rect
        scale = self.zoom_level
        return (x0 * scale, y0 * scale, x1 * scale, y1 * scale)
        
    def next_search(self):
        """Go to next search result"""
        if self.search_results:
            self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
            self.jump_to_search_result()
            
    def prev_search(self):
        """Go to previous search result"""
        if self.search_results:
            self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
            self.jump_to_search_result()
            
    def load_pdf(self):
        """Open file dialog and load PDF"""
        print("Opening file dialog for PDF selection...")
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        print(f"Selected file path: {file_path}")
        
        if file_path:
            self.load_pdf_file(file_path)
        else:
            print("No file selected")
            
    def load_pdf_file(self, file_path):
        """Load PDF from file path"""
        print(f"Loading PDF file: {file_path}")
        try:
            # Load PDF in thread to avoid blocking UI
            def load_thread():
                try:
                    if fitz is None:
                        error_msg = "PyMuPDF (fitz) is not available. Please ensure it is properly installed."
                        print(error_msg)
                        self.after(0, lambda: messagebox.showerror("Error", error_msg))
                        return
                        
                    print(f"Opening PDF document: {file_path}")
                    self.pdf_document = fitz.open(file_path)
                    self.total_pages = len(self.pdf_document)
                    self.current_page = 0
                    print(f"Successfully loaded PDF with {self.total_pages} pages")
                    
                    # Update UI in main thread
                    self.after(0, self.display_current_page)
                    self.after(0, self.update_toolbar)
                    
                    # Call callback if set
                    if self.pdf_loaded_callback:
                        print("Calling PDF loaded callback")
                        self.after(0, self.pdf_loaded_callback)
                    
                except Exception as e:
                    error_msg = f"Failed to load PDF: {str(e)}"
                    print(error_msg)
                    print(f"Traceback: {traceback.format_exc()}")
                    self.after(0, lambda: messagebox.showerror("Error", error_msg))
            
            thread = threading.Thread(target=load_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            error_msg = f"Failed to load PDF: {str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def display_current_page(self):
        """Display the current page"""
        if not self.pdf_document:
            return
            
        try:
            # Get page
            page = self.pdf_document[self.current_page]
            
            # Calculate zoom to fit canvas (only on first load)
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1 and self.zoom_level == 1.0:
                # Calculate zoom to fit
                page_rect = page.rect
                width_zoom = (canvas_width - 20) / page_rect.width
                height_zoom = (canvas_height - 20) / page_rect.height
                self.zoom_level = min(width_zoom, height_zoom) * 0.8  # 80% of fit
            
            # Render page with current zoom level
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=mat)
            
            # Check if PIL modules are available
            if Image is None or ImageTk is None:
                error_msg = "PIL modules are not available. Please ensure Pillow is properly installed."
                print(error_msg)
                messagebox.showerror("Error", error_msg)
                return
                
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Clear canvas and display
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=photo)
            
            # Keep reference
            self.current_photo = photo
            
            # Update scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display page: {str(e)}")
            
    def update_toolbar(self):
        """Update toolbar with current page info"""
        if self.pdf_document:
            self.page_label.config(text=f"Page {self.current_page + 1} of {self.total_pages}")
            self.prev_btn.config(state="normal" if self.current_page > 0 else "disabled")
            self.next_btn.config(state="normal" if self.current_page < self.total_pages - 1 else "disabled")
        else:
            self.page_label.config(text="No PDF loaded")
            self.prev_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
            
    def next_page(self):
        """Go to next page"""
        if self.pdf_document and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_current_page()
            self.update_toolbar()
            # Clear search highlights when changing pages
            self.clear_search_highlights()
            
    def prev_page(self):
        """Go to previous page"""
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.display_current_page()
            self.update_toolbar()
            # Clear search highlights when changing pages
            self.clear_search_highlights()
            
    def zoom_in(self):
        """Zoom in"""
        print("Zoom in button clicked!")  # Debug
        old_zoom = self.zoom_level
        self.zoom_level *= 1.2
        if self.pdf_document:
            self.display_current_page()
            print(f"Zoomed in: {old_zoom:.2f} -> {self.zoom_level:.2f}")
        else:
            print("No PDF document loaded")
            
    def zoom_out(self):
        """Zoom out"""
        print("Zoom out button clicked!")  # Debug
        old_zoom = self.zoom_level
        self.zoom_level /= 1.2
        if self.pdf_document:
            self.display_current_page()
            print(f"Zoomed out: {old_zoom:.2f} -> {self.zoom_level:.2f}")
        else:
            print("No PDF document loaded") 