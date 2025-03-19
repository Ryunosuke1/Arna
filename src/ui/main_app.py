"""
Manus Agent UI - Main Application

This module provides the main screen for the desktop application using Kivy and KivyMD.
"""

import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.splitter import Splitter
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.treeview import TreeView
from kivy.uix.label import Label
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast

# Import internal modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.agent_core import AgentManager
from tools.code_structure import CodeStructureManager


class ProjectView(BoxLayout):
    """View to display project structure"""
    
    def __init__(self, **kwargs):
        super(ProjectView, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.code_structure_manager = CodeStructureManager()
        
        # Add label for project information
        from kivymd.uix.label import MDLabel
        self.project_info = MDLabel(
            text="Project: None",
            halign="center",
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.project_info)
        
        # Add TreeView for project structure
        from kivy.uix.treeview import TreeView
        self.tree_view = TreeView(
            size_hint=(1, 1),
            hide_root=False,
            indent_level=16
        )
        self.tree_view.root_options = {"text": "Project Structure"}
        self.add_widget(self.tree_view)
    
    def update_project_view(self, project_data):
        """
        Update project view
        
        Args:
            project_data: Project data
        """
        if project_data:
            self.project_info.text = f"Project: {project_data.get('name', 'None')}"
            # Update TreeView (in actual implementation, this would be more complex)
            self.tree_view.clear_widgets()
            # Add project structure to TreeView


class CodeEditor(BoxLayout):
    """Code editor providing code editing functionality"""
    
    def __init__(self, **kwargs):
        super(CodeEditor, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Editor header section
        header = BoxLayout(
            size_hint_y=None,
            height=50
        )
        
        from kivymd.uix.label import MDLabel
        self.file_label = MDLabel(
            text="File: None",
            halign="left"
        )
        header.add_widget(self.file_label)
        
        from kivymd.uix.button import MDIconButton
        save_button = MDIconButton(
            icon="content-save",
            on_release=self.save_file
        )
        header.add_widget(save_button)
        
        self.add_widget(header)
        
        # Code editor section
        from kivy.uix.codeinput import CodeInput
        from pygments.lexers.python import PythonLexer
        self.code_input = CodeInput(
            lexer=PythonLexer(),
            size_hint=(1, 1)
        )
        self.add_widget(self.code_input)
        
        self.current_file = None
    
    def load_file(self, file_path):
        """
        Load a file
        
        Args:
            file_path: File path
        """
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                self.code_input.text = f.read()
            self.current_file = file_path
            self.file_label.text = f"File: {os.path.basename(file_path)}"
    
    def save_file(self, instance=None):
        """
        Save a file
        
        Args:
            instance: Button instance (optional)
        """
        if self.current_file:
            with open(self.current_file, 'w') as f:
                f.write(self.code_input.text)
            toast(f"File saved: {os.path.basename(self.current_file)}")


class OutputConsole(BoxLayout):
    """Console to display output and logs"""
    
    def __init__(self, **kwargs):
        super(OutputConsole, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Console header
        header = BoxLayout(
            size_hint_y=None,
            height=50
        )
        
        from kivymd.uix.label import MDLabel
        header.add_widget(MDLabel(
            text="Output Console",
            halign="left"
        ))
        
        from kivymd.uix.button import MDIconButton
        clear_button = MDIconButton(
            icon="delete",
            on_release=self.clear_console
        )
        header.add_widget(clear_button)
        
        self.add_widget(header)
        
        # Console output section
        from kivy.uix.textinput import TextInput
        self.console_output = TextInput(
            readonly=True,
            multiline=True,
            size_hint=(1, 1)
        )
        self.add_widget(self.console_output)
    
    def append_output(self, text):
        """
        Append output to console
        
        Args:
            text: Text to append
        """
        self.console_output.text += text + "\n"
        # Auto-scroll
        self.console_output.cursor = (0, len(self.console_output.text))
    
    def clear_console(self, instance=None):
        """
        Clear console
        
        Args:
            instance: Button instance (optional)
        """
        self.console_output.text = ""


class ManusAgentUI(BoxLayout):
    """Main user interface for Manus Agent"""
    
    def __init__(self, **kwargs):
        super(ManusAgentUI, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Initialize agent manager
        self.agent_manager = AgentManager()
        self.code_structure_manager = CodeStructureManager()
        
        # Toolbar
        self.toolbar = MDTopAppBar(
            title="Manus Agent",
            elevation=10,
            right_action_items=[
                ["folder-open", lambda x: self.show_file_manager()],
                ["cog", lambda x: self.show_settings()],
                ["help", lambda x: self.show_help()]
            ]
        )
        self.add_widget(self.toolbar)
        
        # Main content area
        main_content = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 1)
        )
        
        # Left: Project view
        left_panel = Splitter(
            sizable_from='right',
            min_size=200,
            max_size=400,
            size_hint=(0.3, 1)
        )
        self.project_view = ProjectView()
        left_panel.add_widget(self.project_view)
        main_content.add_widget(left_panel)
        
        # Right: Editor and console
        right_panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.7, 1)
        )
        
        # Editor
        self.code_editor = CodeEditor(
            size_hint=(1, 0.7)
        )
        right_panel.add_widget(self.code_editor)
        
        # Console
        self.output_console = OutputConsole(
            size_hint=(1, 0.3)
        )
        right_panel.add_widget(self.output_console)
        
        main_content.add_widget(right_panel)
        self.add_widget(main_content)
        
        # Bottom: Action buttons
        bottom_panel = BoxLayout(
            size_hint_y=None,
            height=50,
            padding=[10, 5]
        )
        
        new_project_button = MDRaisedButton(
            text="New Project",
            on_release=self.create_new_project
        )
        bottom_panel.add_widget(new_project_button)
        
        generate_code_button = MDRaisedButton(
            text="Generate Code",
            on_release=self.generate_code
        )
        bottom_panel.add_widget(generate_code_button)
        
        run_button = MDRaisedButton(
            text="Run",
            on_release=self.run_code
        )
        bottom_panel.add_widget(run_button)
        
        self.add_widget(bottom_panel)
        
        # File manager
        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_path
        )
    
    def show_file_manager(self):
        """Show file manager"""
        self.file_manager.show(os.path.expanduser("~"))
    
    def exit_file_manager(self, *args):
        """Close file manager"""
        self.file_manager.close()
    
    def select_path(self, path):
        """
        Handle path selection in file manager
        
        Args:
            path: Selected path
        """
        self.exit_file_manager()
        if os.path.isfile(path):
            self.code_editor.load_file(path)
        else:
            toast(f"Directory selected: {path}")
    
    def show_settings(self):
        """Show settings screen"""
        toast("Settings screen (not implemented)")
    
    def show_help(self):
        """Show help screen"""
        toast("Help screen (not implemented)")
    
    def create_new_project(self, instance):
        """
        Create a new project
        
        Args:
            instance: Button instance
        """
        # In actual implementation, show a dialog to input project name and description
        project_name = "Sample Project"
        project_description = "Sample project description"
        
        project_data = self.code_structure_manager.create_project(
            project_name, 
            project_description
        )
        
        self.project_view.update_project_view(project_data)
        self.output_console.append_output(f"Created new project '{project_name}'")
    
    def generate_code(self, instance):
        """
        Generate code
        
        Args:
            instance: Button instance
        """
        # In actual implementation, generate code from project data
        self.output_console.append_output("Starting code generation...")
        
        try:
            output_dir = os.path.join(os.path.expanduser("~"), "generated_code")
            os.makedirs(output_dir, exist_ok=True)
            
            generated_files = self.code_structure_manager.generate_code(output_dir)
            
            for file_path in generated_files:
                self.output_console.append_output(f"Generated file: {file_path}")
                
            if generated_files:
                self.code_editor.load_file(generated_files[0])
        except Exception as e:
            self.output_console.append_output(f"Error: {str(e)}")
    
    def run_code(self, instance):
        """
        Run code
        
        Args:
            instance: Button instance
        """
        self.output_console.append_output("Run code (not implemented)")


class ManusAgentApp(MDApp):
    """Manus Agent application"""
    
    def build(self):
        """Build application"""
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"
        
        return ManusAgentUI()


if __name__ == "__main__":
    ManusAgentApp().run()
