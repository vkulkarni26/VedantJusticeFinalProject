from openai import OpenAI
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QVBoxLayout, QPushButton, QWidget, QTabWidget, QLabel
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import sys
client = OpenAI(api_key = "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")


class ChatApp(QMainWindow):
    def __init__(self, identity, image_id):
        super().__init__()
        self.image_present = False
        self.identity = identity
        self.image_id = image_id
        
        # Create a QTextEdit widget for displaying the chat
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        # Create a QLineEdit widget for user input
        self.user_input = QLineEdit()
        # Create a QPushButton for sending user input

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        # Bind the <Return> key event to the send_message method
        self.user_input.returnPressed.connect(self.send_message)



        # Create a QVBoxLayout to arrange widgets
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.chat_display)
        self.layout.addWidget(self.user_input)
        self.layout.addWidget(send_button)
        
        
        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)
   

    def send_message(self):
        # Get user input from the QLineEdit widget
        user_message = self.user_input.text()

        id = self.identity

        # Display user's message in the chat
        self.display_message("You: " + user_message)

        # Generate AI response
        ai_id = self.response_prompt_gen(id)

        ai_response = self.generate_response(user_message, ai_id)

        image_prompt = self.generate_image_prompt(ai_response)

        # Display AI's response in the chat
        self.display_message("AI: " + ai_response)
        if self.image_present:
            self.image_widget.deleteLater()
            self.image_present = False

        if self.image_id == "":
            image_url = self.generate_image("Create image panels equal to the last number in the explanation of a given topic. In each panel, create an infographic type image that visually explains the topic corresponding to its numbered panel. do this for each panel in the list of panels. Here is the given topic: " + image_prompt)

        else:
            image_maker = self.image_prompt_gen(self.image_id, image_prompt)
            image_url = self.generate_image(image_maker)

        self.image_widget = ImageWidget(image_url)

        self.layout.addWidget(self.image_widget)
        self.image_present = True

        print("AI Maker Prompt: " + ai_id)
        print("Numbered List: " + image_prompt)
        print("Image Prompt: " + image_maker)

        # Clear the user input
        self.user_input.clear()

    def display_message(self, message):
        # Display a message in the chat
        current_text = self.chat_display.toPlainText()
        self.chat_display.setPlainText(current_text + message + "\n")
    
    def response_prompt_gen(self, input):
        completion = client.chat.completions.create(
          model="gpt-4",
          messages=[
          {"role": "system", "content": "Develop an AI with a focus on optimizing prompts for the 'role': 'system', 'content': area. Instruct the AI to understand and generate prompts that are clear, concise, and effectively guide other AIs in providing relevant and accurate information. Emphasize the importance of encouraging creativity and adaptability in the prompts while maintaining a balance between specificity and generality. The goal is to enhance the capability of other AIs to produce high-quality responses within the 'role': 'system', 'content': context."},
          {"role": "user", "content": "Create a good prompt for the 'role':'system','content': area of the openai API that will generate an AI that matches the personality described in this description: " + input}
          ]
        )

        # Extract and return the generated response
        return completion.choices[0].message.content

    def generate_response(self, prompt, gptid):
        # Call the OpenAI API to generate a response
        completion = client.chat.completions.create(
          model="gpt-4",
          messages=[
          {"role": "system", "content": gptid},
          {"role": "user", "content": prompt}
          ]
        )

        # Extract and return the generated response
        return completion.choices[0].message.content
    
    def generate_image_prompt(self, gpt_prompt):
        completion = client.chat.completions.create(
            model ="gpt-4",
            messages = [
            {"role": "system", "content": "You are an excellent summarizer that can distill information to their most important points and create a numbered list enumerating each of those important points."},
            {"role": "user", "content": "create a numbered list describing all the important points in this statement" + gpt_prompt}
            ]
        )

        return completion.choices[0].message.content
    
    def image_prompt_gen(self, image_style, image_topic):
        completion = client.chat.completions.create(
            model ="gpt-4",
            messages = [
            {"role": "system", "content": "Train the AI to generate highly specific DALL-E prompts based on a list of descriptors. Instruct the AI to understand and represent each descriptor in the list accurately within the generated image. Encourage the AI to consider the spatial relationships and visual details associated with each descriptor. Ensure that the prompts lead to images that vividly portray the combined elements listed. Prioritize clarity and precision in the generated prompts to achieve a one-to-one correspondence between the descriptors and the visual elements in the resulting DALL-E images."},
            {"role": "user", "content": "Create a dall-e prompt that would generate an image that informs the user about this topic: " + image_topic + ". Use this image style: " + image_style + ". Make sure that the prompt makes the dall-e AI understand exactly what you are trying to make it create using specific language, visual details, and encourage the ai to consider spatial relationships"}
            ]
        )

        return completion.choices[0].message.content
    
    def generate_image(self, banterid):
        response = client.images.generate(
            model="dall-e-3",
            prompt=banterid,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        print("Image Request Called")
        return response.data[0].url
    
    


class ImageWidget(QWidget):
    def __init__(self, image_url):
        super().__init__()

        self.image_label = QLabel(self)

        # Load the image from the URL
        self.load_image_from_url(image_url)
        print("Image Loaded")
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)
        

    def load_image_from_url(self, image_url):
        manager = QNetworkAccessManager(self)
        request = QNetworkRequest(QUrl(image_url))
        print("Image Request Processed")
        reply = manager.get(request)

        reply.finished.connect(lambda: self.handle_image_load(reply))
        print("Image Request Handling")

    def handle_image_load(self, reply):
        try:
            if reply.error() == QNetworkReply.NoError:
                print("No Image Error")
                data = reply.readAll()
                image = QImage.fromData(data)
                pixmap = QPixmap.fromImage(image)
                self.image_label.setPixmap(pixmap)
                self.image_label.setAlignment(Qt.AlignCenter)
                print("Image Request Handled")
            else:
                print("Error loading image:", reply.errorString())
        except Exception as e:
            print("Exception in handle_image_load:", e)
        finally:
            print("All good in the neighborhood")


class TabbedApp(QMainWindow):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        #Stock Bots
        stock_label = QLabel("Click one of the stock bots, or consider creating your own personal banter bot!", self)
        layout.addWidget(stock_label)
        
        add_char_button = QPushButton("Add Charisma Bot", self)
        add_char_button.clicked.connect(self.add_char_bot)
        layout.addWidget(add_char_button)

        add_can_button = QPushButton("Add Candor Bot", self)
        add_can_button.clicked.connect(self.add_can_bot)
        layout.addWidget(add_can_button)
        
        #Title Input for Bot Creator
        title_label = QLabel("Enter the title for your new banter bot:", self)
        layout.addWidget(title_label)

        self.title_line_edit = QLineEdit(self)
        layout.addWidget(self.title_line_edit)

        #Description Input for Bot Creator
        desc_label = QLabel("Enter the description of the tone for your new banter bot:", self)
        layout.addWidget(desc_label)

        self.desc_line_edit = QLineEdit(self)
        layout.addWidget(self.desc_line_edit)

        #Image Type Input for Bot Creator
        image_desc_label = QLabel("Enter the image type you would like your banter bot to show you:", self)
        layout.addWidget(image_desc_label)

        self.image_desc_line_edit = QLineEdit(self)
        layout.addWidget(self.image_desc_line_edit)

        #Button to Add A Bot
        add_tab_button = QPushButton("Add Banter Bot", self)
        add_tab_button.clicked.connect(self.add_new_tab)
        layout.addWidget(add_tab_button)


        #Set the Widget and Layout for the Bot Creator

        creator_widget = QWidget()
        creator_widget.setLayout(layout)


        self.setWindowTitle("Banter Bot")

        # Create the tab widget
        self.tab_widget = QTabWidget(self)

        #charisma_id = "You are a charismatic assistant who has the ability to attract other people's appreciation and regard effortlessly. You should use your natural charisma to help the user and make them happy"
        #charisma_url_id = ""
        # Create the first tab with a charismatic personality
        #tab1 = ChatApp(charisma_id, charisma_url_id)

        # Create the second tab with a succinct personality

        #candor_id = "You are a clear and concise assistant who says exactly what you mean. You have incredible candor and clarity"
        #candor_url_id = ""
        #tab2 = ChatApp(candor_id, candor_url_id)
        


        # Add the tabs to the tab widget
        self.tab_widget.addTab(creator_widget, "Bot Creator")
        #self.tab_widget.addTab(tab1, "Charisma Bot")
        #self.tab_widget.addTab(tab2, "Candor Bot")
        


        # Set the tab widget as the central widget
        self.setCentralWidget(self.tab_widget)
        

    def generate_image(self, banterid):
        response = client.images.generate(
            model="dall-e-3",
            prompt=banterid,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        print("Image Request Called")
        return response.data[0].url
    
    def add_new_tab(self):
        title_input = self.title_line_edit.text()
        desc_input = self.desc_line_edit.text()
        image_desc_input = self.image_desc_line_edit.text()

        new_tab = ChatApp(desc_input, image_desc_input)
        # Add the new tab to the main tab widget
        self.tab_widget.addTab(new_tab, title_input)

        self.title_line_edit.clear()
        self.desc_line_edit.clear()
        self.image_desc_line_edit.clear()
        
        
        print("New Tab Added")
    
    def add_char_bot(self):

        desc = "charismatic and endearing"
        image = "romantic era image style"
        title = "Charisma Bot"

        new_tab = ChatApp(desc, image)
        self.tab_widget.addTab(new_tab, title)

        print("Stock Tab Added")
    
    def add_can_bot(self):

        desc = "clear and concise"
        image = "infographic image style"
        title = "Candor Bot"

        new_tab = ChatApp(desc, image)
        self.tab_widget.addTab(new_tab, title)

        print("Stock Tab Added")
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TabbedApp()
    window.show()
    sys.exit(app.exec_())