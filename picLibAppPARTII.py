#Parte 2 de projeto PicLib

#Faculty of Sciences of the University of Lisbon n 57658 David Tavares Ribeiro 
import os
import shutil
from picLibClassesPART1 import ImageCollection, TagCollection, Tag
from kivy.app import App
from zipfile import ZipFile
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner as spin

from kivy.core.window import Window as Win
from kivy.graphics import Rectangle, Color
from kivy.uix.filechooser import FileChooserListLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.config import Config
from kivy.uix.stacklayout import StackLayout


#########################################################################################################################################################


#This class is a superclass of the configuration classes that handle the suggested app configuration elements (configuration A, B, C).
class configuration(BoxLayout):
    def __init__(self, library, mainScreen, objects, **kwargs):
        super().__init__(**kwargs)
        self.library = library
        self.mainScreen = mainScreen
        self.objects = objects
        self.page = 0
        self.manypage = []
        self.orientation = 'horizontal'
        self.buttonbar = BoxLayout(orientation = 'vertical', size_hint= (0.1, 1))
        self.config = BoxLayout(size_hint= (0.8, 1))
        self.buttons = []
        self.selectedbutton = []
        self.quant = 4
        self.pageimages = 5
        self.add_widget(self.buttonbar)
        self.add_widget(self.config)
        Win.size = (1000, 800)
    
    def createRows(self):    
        self.quant = len(self.objects)
        self.buttons = []
        self.selectedbutton = []
        self.page = 0
        npages = int((self.quant-1)/self.pageimages) + 1
        self.manypage = [StackLayout(spacing = 4, orientation = 'lr-tb' , padding = 8) for i in range(npages)]
        self.fillRows()

        
        self.showPage()

    def fillRows(self):
        for item in self.objects:
            newbutton = ToggleButton(size_hint = (0.2, 0.2))
            newbutton.text = item.getName()
            newbutton.tag = item
            self.buttons.append(newbutton)

    def showPage(self):
        self.config.clear_widgets()
        self.config.add_widget(self.manypage[self.page])

    def getbuttons(self):
        return self.buttons

    def getselectedbutton(self):
        return self.selectedbutton
    

#
class ChooseFolder(BoxLayout):
    def __init__(self, library, configuration, **kwargs):
        super().__init__(**kwargs)
        self.library = library
        self.configuration = configuration
        self.loadbutton = Button(text='Open Loaded Collection', on_press = self.library.pl.importcollect)
        self.openbutton = Button(text='Open New Collection', on_press = self.ChooseDir)
        self.add_widget(self.openbutton)
        self.add_widget(self.loadbutton)

    def ChooseDir(self, but):
        content = BoxLayout(orientation = 'vertical', spacing = 5)
        self.directorypopup = Popup(title = 'open folder', content = content, size_hint = (0.7, 0.7))
        self.textinput = FileChooserListLayout(path = os.getcwd(), dirselect = True)
        buttons = BoxLayout(size_hint_y = None, height = '45', spacing = '4')
        okbutton = Button(text = 'Ok', on_release=self.validate)
        buttonCancel = Button(text = 'Cancel', on_release = self.directorypopup.dismiss)
        content.add_widget(self.textinput)
        content.add_widget(buttons)
        buttons.add_widget(okbutton)
        buttons.add_widget(buttonCancel)
        self.directorypopup.open()

    def validate(self, button):
        self.dir = self.textinput.path
        content = BoxLayout( height = '45', orientation = 'horizontal', spacing = '4', size_hint_y = None)
        self.confirmpopup = Popup(title = 'confirm directory' + str(self.dir), content = content, size_hint = (0.6, 0.6))
        okbutton = Button(text = 'Ok', on_release = self.createImageCollection)
        buttonCancel = Button(text = 'Cancl', on_release = self.confirmpopup.dismiss)
        content.add_widget(okbutton)
        content.add_widget(buttonCancel)
        self.confirmpopup.open()

    def createImageCollection(self, button):
        try: 
            self.library.pl.createCollection(self.dir)
            self.directorypopup.dismiss()
            self.confirmpopup.dismiss()
            self.configuration.config.remove_widget(self.configuration.chooseFolder)
        except Exception as ex:
            self.confirmpopup.title = str(ex)
            button.bind(on_release = self.confirmpopup.dismiss)


#Na configuração A, quando uma (e apenas uma) imagem está selecionada, o painel BottomRow deve mostrar os tags associados 
#à imagem bem como a sua data. A medida que as imagens estão selecionadas, o número de imagens na seleção é mostrado no painel BottomRow. 

#Na configuração A existe outro botão «-T» cujo funcionamento é semelhante e que serve para remover tags associadas a imagens.
# Na configuração A, um botão «T» permite transitar para a configuração C onde pode-se fazer a gestão dos tags.  


class configurationA(configuration):

    def __init__(self, library, mainScreen, objects, **kwargs):
        super().__init__(library, mainScreen, objects, **kwargs)
        self.imgcol = objects
        self.addTagtoimgbutton = Button(text = '+T', on_release = self.addTagbutton)
        self.rotateimgbutton = Button(text = 'R90', on_release = self.rotateimg)
        self.removeTagtoimgbutton = Button(text = '-T', on_release = self.removeTagbutton)

        self.compressbutton = Button(text = 'Zip', on_release = self.SaveZip)
        self.searchbutton = Button(text = 'S', on_release = mainScreen.loadsearchconfig)
        self.Tagbutton = Button(text = 'Tags', on_release = mainScreen.loadconfigurationC)
        self.chooseFolder = ChooseFolder(library, self, size_hint= (1,0.2))
        self.config.add_widget(self.chooseFolder)
        self.buttonbar.add_widget(self.Tagbutton)
        self.buttonbar.add_widget(self.searchbutton)
     
    
    def fillRows(self):
        for img in self.objects:
            newbutton = ImageBox(img, self.pageimages, on_release = self.selectedim)
            self.buttons.append(newbutton)
        
    def removeTagbutton(self, button):
        self.add = False
        self.mainScreen.loadconfigurationB()

    def addTagbutton(self, button):
        self.add = True
        self.mainScreen.loadconfigurationB()
        
    def rotateimg(self, rotatebutton):
        button = self.selectedbutton[0]
        button.image.rotate()
        button.background_color = (1 ,1,1,1)
        button.background_normal =  button.image.getImagefile()
        button.background_down = button.background_normal
        self.selectedbutton = []
        button.state = 'normal'

        self.createRows()
        self.refreshbuttonbar()


    def getfullImgcol(self):
        return self.imgcol
    def SaveZip(self, button):
        savezip = SaveZip(self, self.library, title = 'Save as', size_hint = (0.8, 0.8))
        savezip.open()

    def refreshbuttonbar(self):
        self.buttonbar.remove_widget(self.addTagtoimgbutton)
        self.buttonbar.remove_widget(self.removeTagtoimgbutton)
        self.buttonbar.remove_widget(self.compressbutton)
        self.buttonbar.remove_widget(self.rotateimgbutton)
        self.library.bottomRow.remove_widget(self.library.bottomRow.datebutton)
        self.library.bottomRow.settextInfo('')
        
        if len(self.selectedbutton) > 0:
            self.buttonbar.add_widget(self.addTagtoimgbutton)
            self.buttonbar.add_widget(self.removeTagtoimgbutton)
            self.buttonbar.add_widget(self.compressbutton)
        if len(self.selectedbutton) == 1: 
            img = self.selectedbutton[0].getImage()
            self.library.bottomRow.addDatebutton(img.getDate())    
            self.buttonbar.add_widget(self.rotateimgbutton)
            for tag in img.metadata['tags']: self.library.bottomRow.infotext('{}, '.format(tag)) 

#
class configurationB(configuration):

    def __init__(self, library, mainScreen, objects, **kwargs):
        super().__init__(library, mainScreen, objects, **kwargs)
        self.createRows()
        self.tagok = Button(text='Ok', on_release = self.taggedimage)
        self.buttonbar.add_widget(self.tagok)
        self.backbutton = Button(text='<-', on_release = self.mainScreen.loadconfigurationA)
        self.buttonbar.add_widget(self.backbutton)

    def taggedimage(self, button):
        configurationAselbuttons = self.mainScreen.configurationA.getselectedbutton()

        self.selectedbutton = []
        for button in self.buttons:
            if button.state is 'down': self.selectedbutton.append(button.tag)
        for button in configurationAselbuttons:
            for tag in self.selectedbutton:
                img = button.image
                if self.mainScreen.configurationA.add: img.addTag(tag)
                elif img.hasTag(tag): img.removeTag(tag)

        return self.mainScreen.loadconfigurationA()

# A configuração C mostra a coleção de tags. O botão «+T» permite adicionar um tag à coleção. Para isso, passa para a configuração D onde o utilizador pode indicar o nome do tag a adicionar. Na configuração D, o botão «OK» confirma a adição do novo tag (e efetivamente o adiciona à coleção) e volta à configuração C. 
# O botão «<» permite voltar atrás, anulando a operação. Ainda na configuração C o botão «<» cancela a operação de adição de tag e volta à configuração anterior (A). 
class configurationC(configuration):

    def __init__(self, library, mainScreen, objects, **kwargs):
        super().__init__(library, mainScreen, objects, **kwargs)
        self.createRows()
        self.textinputbox = BoxLayout()
        self.directorypopup = Popup(title = 'Please Enter Tag name', content = self.textinputbox, size_hint = (0.5, 0.2))
        self.textinput = TextInput(multiline = False, on_text_validate = self.saveNewTag)

        self.addTagtocolbutton = Button(text='+T', on_release = self.directorypopup.open)
        self.backbutton = Button(text='<', on_release = self.mainScreen.loadconfigurationA)
        self.textinputbox.add_widget(self.textinput)
        self.buttonbar.add_widget(self.addTagtocolbutton)
        self.buttonbar.add_widget(self.backbutton)

    def saveNewTag(self, textinput):
        newtag = Tag(textinput.text)        
        collectionTag = self.library.pl.getcollectionTag()
        collectionTag.registerItem(newtag)
        self.mainScreen.updateTags(newtag)
        textinput.text = ''
        self.directorypopup.dismiss()

#allows for the search of previously tagged images
class searchconfig(configurationB):
    def __init__(self, library, mainScreen, objects, **kwargs):
        super().__init__(library, mainScreen, objects, **kwargs)

    def taggedimage(self, button):
        configurationA = self.mainScreen.getconfigurationA()   
        self.selectedbutton = []
        for button in self.buttons:
            if button.state == 'down': self.selectedbutton.append(button.tag)
        if len(self.selectedbutton) == 0:
            configurationA.objects = configurationA.getfullImgcol()
            configurationA.createRows()
        else:
            taggedbuttons = set() #usando um set

            for button in configurationA.getbuttons():
                for tag in self.selectedbutton:
                    if button.image.hasTag(tag): taggedbuttons.add(button.image)
            configurationA.objects = taggedbuttons
            configurationA.createRows()  
        self.mainScreen.loadconfigurationA()
        
#displays the image
class ImageBox(ToggleButton):
    def __init__(self, cpimage, ratio, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.height = 180 - ratio * 3
        self.width = self.height * cpimage.getRatio() 
        self.image = cpimage
        self.background_color = (1,1,1 ,1)       #ver se é preciso
        self.background_normal = cpimage.getImagefile()
        self.background_down = self.background_normal

    def getImage(self):
        return self.image
Config.set('graphics', 'window_state', 'maximized')

#allows for saving iles in zip folders
class SaveZip(Popup):

    def __init__(self, configurationA, library, **kwargs):
        super().__init__(**kwargs)
        self.configurationA = configurationA
        self.library = library
        self.content = content = BoxLayout(orientation = 'vertical', spacing = 5)
        self.dirinput = FileChooserListLayout(path = os.getcwd(), dirselect = True)
        bottom = BoxLayout(height = '45', spacing = '4', size_hint_y = None)
        self.nameinput = TextInput(multiline = False, size_hint = (0.7, 1), on_text_validate = self.savezip)
        savebutton = Button(text = 'Save', size_hint = (0.2, 1), on_release = self.savezip)
        content.add_widget(self.dirinput)
        content.add_widget(bottom)
        bottom.add_widget(self.nameinput)
        bottom.add_widget(savebutton)

    def savezip(self, button):
        savename = self.nameinput.text      
        if savename == None:
            self.title = 'Please choose name'
        else:
            self.library.pl.imgcol.saveCollection()
            self.library.pl.collectionTag.saveCollection()
            with ZipFile('{}.zip'.format(savename), 'w') as zip_object:
                for butt in self.configurationA.getselectedbutton():
                    filename = butt.image.getImagefile()
                    zip_object.write(filename, arcname = os.path.basename(filename))                    #is it working
            self.dismiss()


class PicLib_Picture_Library(App):
    

    #def __init__()
    def build(self):
        self.imgcol = ImageCollection('imgcol')
        self.collectionTag = TagCollection('collectionTag')
        self.library = PicLibconfiguration(self, orientation = 'vertical', spacing = 2)
        Win.bind(on_request_close = self.on_request_close)
        return self.library
    
    def saveCollect(self, button):
        self.imgcol.saveCollection()
        self.collectionTag.saveCollection()
        self.stop()

    def on_request_close(self, button):
        content = BoxLayout( spacing = '5', orientation = 'horizontal')
        button2 = Button(text='Yes', size_hint= (1, 0.2), on_release = self.saveCollect)
        button1 = Button(text='No', size_hint= (1, 0.2), on_release = self.stop) 
        popup = Popup(title='Save Collection?', content = content, size_hint= (None, None), size= (700, 300))
        content.add_widget(button2)
        content.add_widget(button1)
        popup.open()
        return True


    def importcollect(self, button):
        try:
            self.imgcol.loadCollection()
            self.collectionTag.loadCollection()
            self.library.mainScreen.configurationB.createRows()
            self.library.mainScreen.configurationC.createRows()
            self.library.mainScreen.searchconfig.createRows()
            # ??
            self.library.mainScreen.configurationA.createRows()
        except FileNotFoundError: 
            popup = Popup(title = '404 Image Collection Not Found!', size_hint = (0.7, 0.1))
            popup.open()

    def getcollectionTag(self):
        return self.collectionTag

    def createCollection(self, imagesdir):
        if os.path.exists('collectionsRootFolder/'): 
            shutil.rmtree('collectionsRootFolder/')
        if os.path.exists(self.imgcol.filename + '.json'): 
            os.remove(self.imgcol.filename + '.json')
        if os.path.exists(self.collectionTag.filename + '.json'): 
            os.remove(self.collectionTag.filename + '.json')
        self.imgcol.scanFolder(imagesdir)
        self.library.mainScreen.configurationA.createRows()


#A janela da aplicação está dividida em 3 zonas arranjadas verticalmente: 

#a linha de cima com o nome da aplicação (que vamos chamar TopRow)
#a linha de baixo com a cor castanha (que vamos chamar BottomRow)
#a zona principal no meio.

#draws the different configuration elements
class PicLibconfiguration(BoxLayout):
    def __init__(self, pl, **kwargs):
        super().__init__(**kwargs)
        self.topRow = Label(text='PicLib Picture Library', font_size = 40, size_hint= (1, 0.1),  color= (0.2 ,0.2,0.2,1))
        self.pl = pl
        self.mainScreen = mainScreen(self, pl, size_hint= (1, 0.9), orientation = 'horizontal') 
        self.bottomRow = BottomRow(self, size_hint= (1, 0.1), orientation = 'horizontal')
        self.add_widget(self.topRow)
        self.add_widget(self.mainScreen)
        self.add_widget(self.bottomRow)
        with self.canvas.before:
            Color(0.7, 0.7, 0.7)
            Rectangle(pos=(0, 725), size=(1000, 400))

    def getmainScreen(self):
        return self.mainScreen






#uses the spin widget to change hte number of display images, shows tags and date, and draws bottom buttons
class BottomRow(BoxLayout):

    def __init__(self, library, **kwargs):
        super().__init__(**kwargs,)
        self.library = library
        self.mainScreen = library.getmainScreen()
        self.datebutton = Button(size_hint= (0.1, 1), on_press = self.setdate)
        self.info = Label(text='', size_hint= (0.5, 1), font_size=30, color= (0.7 ,0.7,0.7,1))
        self.buttons = BoxLayout(size_hint= (0.3, 1))
        self.previousbutton = Button(size_hint= (0.5, 1), text='<-', on_press = self.previouspage)
        self.nextbutton = Button(size_hint= (0.5, 1), text = '->', on_press = self.nextpage)
        self.choosebutton = spin(text = 'nº', values = (([str(s*(s)) for s in range(1,5)]))) #number of displayed images in button, should work now
        self.choosebutton.bind(text = self.mainScreen.show_selected_value)
        self.buttons.add_widget(self.previousbutton)
        self.buttons.add_widget(self.choosebutton)
        self.buttons.add_widget(self.nextbutton)
        self.add_widget(self.info)
        self.add_widget(self.buttons)
        with self.canvas.before:
            Color(0.6, 0.22, 0.01, 0.6) #rectangulo castanho
            self.rect = Rectangle()
            self.rect.pos = self.pos
            self.rect.size = self.size
        self.bind(pos=BottomRow.displayupdate, size=BottomRow.displayupdate)

    def previouspage(self, button):
        configuration = self.mainScreen.getcurrentconfiguration()
        if configuration.page > 0: 
            configuration.page -= 1
            configuration.showPage()

    def nextpage(self, button):
        configuration = self.mainScreen.currentconfiguration
        if configuration.page < len(configuration.pages)-1: 
            configuration.page += 1
            configuration.showPage()

    @staticmethod
    def displayupdate(instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def setdate(self, button):

        def setmonth(textinput):
            textinputmonth.focus = True

        def setday(textinput):
            textinputday.focus = True
            if len(textinput.text) == 1: 
                textinput.text = '0' + textinput.text

        def checkDate(textinput):   
            textinputyear.focus = True
            if len(textinput.text) == 1: 
                textinput.text = '0' + textinput.text


            try: 
                newdate ='- {}:{}:{}'.format(textinputyear.text, textinputmonth.text, textinput.text)
                self.mainScreen.configurationA.selectedbutton[0].image.setDate(newdate)
                self.datebutton.text = newdate
            except ValueError as error: self.directorypopup.title = 'Invalid Date! (YYYY:MM:DD)' 

#s
        content = BoxLayout(orientation = 'horizontal')
        self.directorypopup = Popup(title = 'Enter Date (YYYY:MM:DD)', content = content, size_hint = (0.5, 0.2))
        textinputyear = TextInput(multiline = False, on_text_validate = setmonth)
        textinputmonth = TextInput(multiline = False, on_text_validate = setday)
        textinputday = TextInput(multiline = False, on_text_validate = checkDate)
        content.add_widget(textinputyear)
        content.add_widget(textinputmonth)
        content.add_widget(textinputday)
        self.directorypopup.open()

    def addDatebutton(self, date):
        self.datebutton.text = date
        self.clear_widgets()
        self.add_widget(self.datebutton)
        self.add_widget(self.info)
        self.add_widget(self.buttons)

    def choicebuttonText(self, text):
        self.choosebutton.text = text

    def infotext(self, text):
        self.info.text += text

    def settextInfo(self, text):
        self.info.text = text

#cria as configurações do painel principal, visuliza imagens
class mainScreen(BoxLayout):

    def __init__(self, library, pl, **kwargs):
        super().__init__(**kwargs)
        self.library = library      
        self.configurationA = configurationA(library, self, pl.imgcol.items)
        self.configurationC = configurationC(library, self, pl.collectionTag.items)
        self.configurationB = configurationB(library, self, pl.collectionTag.items)
        self.searchconfig = searchconfig(library, self, pl.collectionTag.items)
        self.currentconfiguration = self.configurationA
        self.add_widget(self.currentconfiguration)
        Win.clearcolor = (0.6, 0.6, 0.6, 1) #background cinzento


    
    
    def ConfigurationLoad(self):
        self.clear_widgets()
        self.library.BottomRow.choicebuttonText(str(self.currentconfiguration.pageimages))
        for button in self.currentconfiguration.buttons: button.state = 'normal'
        self.currentconfiguration.selectedbutton = []
        if self.currentconfiguration == self.configurationA: self.configurationA.refreshbuttonbar()
        self.add_widget(self.currentconfiguration)
        
    def loadconfigurationA(self, button = None):
        self.currentconfiguration = self.configurationA
        self.ConfigurationLoad()

    def loadconfigurationB(self, button = None):
        self.currentconfiguration = self.configurationB
        self.ConfigurationLoad()


    def loadconfigurationC(self, button = None):
        self.currentconfiguration = self.configurationC
        self.ConfigurationLoad()

    def loadsearchconfig(self, button = None):
        self.currentconfiguration = self.searchconfig
        self.ConfigurationLoad()


    def updateTags(self, newtag):
        self.configurationB.objects.add(newtag)
        self.configurationC.objects.add(newtag)
        self.searchconfig.objects.add(newtag)
        self.configurationB.createRows()
        self.configurationC.createRows()
        self.searchconfig.createRows()
        self.clear_widgets()
        self.add_widget(self.currentconfiguration)
 
    def show_selected_value(self, text, spin):
        if self.currentconfiguration.buttons != []:
            self.currentconfiguration.pageimages = int(text)
            self.currentconfiguration.createRows()

    def getcurrentconfiguration(self):
        return self.currentconfiguration

    def getconfigurationA(self):
        return self.configurationA

if __name__ == '__main__': 
    PicLib_Picture_Library().run()