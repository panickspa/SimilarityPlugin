from qgis.PyQt.QtCore import QObject, pyqtSignal, QVariant

from qgis.core import (
    QgsRasterLayer,
    QgsProject,
    QgsPointXY,
    QgsPoint,
    QgsRaster,
    QgsRasterShader,
    QgsColorRampShader,
    QgsSingleBandPseudoColorRenderer,
    QgsSingleBandColorDataRenderer,
    QgsSingleBandGrayRenderer,
    QgsGeometry,
    Qgis
)

from qgis.gui import QgsQueryBuilder
import datetime
import time
import cv2 as cv

class CalculationRasterModule(QObject):
    """
    Calculation Module for checking the similarity
    
    ..

    Attribute
    -----------
    killed = False
        Killed status object
    layer : QgsRasterLayer
        First original layer
    layerDup : QgsRasterLayer
        First duplicated layer
    layerResult : QgsRasterLayer
        First result layer
    layer2 : QgsRasterLayer
        Second original layer
    layer2Dup : QgsRasterLayer
        Second duplicated layer
    layerResult : QgsRasterLayer
        Second result layer
    method : int
        Method selected
    radius : float
        Determined radius from user
    similarLayer : list=[]
        Similar result
    suffix: str
        Duplicated name suffix layer
    scoreName: str
        Duplicated scoreName attribute
    translate : bool
        Translate status
    treshold : float
        Treshold for calculation
    cumulative : float
        Cumulative score each feature

    """
    killed = False
    layer : QgsRasterLayer
    layerDup : QgsRasterLayer
    layerResult : QgsRasterLayer
    layer2 : QgsRasterLayer
    layer2Dup : QgsRasterLayer
    layerResult2 : QgsRasterLayer
    primaryLayer: list
    primaryLayer2: list
    method : int
    radius : float
    similarLayer = []
    suffix: str
    scoreName: str
    translate : bool
    treshold : float
    cumulative: float
    
    def __init__(self):
        super().__init__()
    
    def setTreshold(self, treshold:float):
        """Set the treshold attribute.

        :param treshold float :Determined treshold from user

        """
        self.treshold = treshold
    
    def setLayers(self, layer:QgsRasterLayer, layer2:QgsRasterLayer):
        """Set the original layers.

        :param layer QgsRasterLayer: The first layer
        :param layer2 QgsRasterLayer: The second layer
        
        """
        self.layer = layer
        self.layer2 = layer2

    def setMethod(self, method:int):
        """Set the choosen method.

        :param method int: The index of choosen method (determined by user)
        
        """
        self.method = method
    
    def setTranslate(self, translate:bool):
        """Set translate status.

        :param translate bool: Translate status
        
        """
        self.translate = translate

    def setRadius(self, radius:float):
        """Set radius.

        :param radius float: Set the radius
        
        """
        self.radius = radius
    
    def setSuffix(self, suffix:str):
        """Set suffix name suffix cloned layer's.

        :param suffix str: Suffix value
        
        """
        self.suffix = suffix
    
    def setScoreName(self, scoreName:str):
        """Set score name attribute cloned layer's.

        :param scoreName str: Score name value

        """
        self.scoreName = scoreName
    
    def getCumulative(self, similar:list):
        """Get Cumulative Score"""
        # score = float(0)
        # scoreMatch = float(0)
        # for i in self.layerResult.getFeatures('"id" = '+str(similar[0])):
        #     score = float(score)+float(i.attribute(self.scoreName))
        # for i in self.layerResult2.getFeatures('"id" = '+str(similar[1])):
        #     scoreMatch = float(scoreMatch)+float(i.attribute(self.scoreName))
        # return [round(score,3), round(scoreMatch, 3)]
    def getSimilarLayer(self):
        """Get the similar layer"""
        return self.similarLayer

    def getLayers(self):
        """get the original layer"""
        return [self.layer, self.layer2]

    def getLayersDup(self):
        """get the duplicated layer"""
        return [self.layerDup, self.layer2Dup]

    def getLayersResult(self):
        """Get the results"""
        return [self.layerResult, self.layerResult2]

    def getSimilarLayer(self):
        """get list of the similar layer"""
        return self.similarLayer

    def getTranslate(self):
        """get translate status"""
        return self.translate
    
    def __getAreaRasterMap(self, feature:QgsRasterLayer):
        """"""
        coord_bb = [ 
            feature.extent().xMinimum(),
            feature.extent().yMinimum(),
            feature.extent().xMaximum(),
            feature.extent().yMaximum()
        ]
        coord_start = QgsPointXY(coord_bb[0], coord_bb[1])
        distances = [
            coord_start.distance(coord_bb[2],coord_bb[1]),
            coord_start.distance(coord_bb[0],coord_bb[3])
        ]
        r_ = (distances[0]/feature.rasterUnitsPerPixelX())
        r2_ = (distances[1]/feature.rasterUnitsPerPixelY())
        # print("radius")
        # print(r_)
        # print(r2_)
        area_counter = 0
        for i in range(0, int(r_)+1):
            for j in range(0, int(r2_)+1):
                """"""
                p_ = QgsPointXY(
                        coord_bb[0]+(feature.rasterUnitsPerPixelX()*i),
                        coord_bb[1]+(feature.rasterUnitsPerPixelY()*j)
                    )
                pixel_data = feature.dataProvider().identify(
                    point = p_,
                    format = Qgis.RasterIdentifyFormat(1)
                ).results()
                a = (
                        (
                            (pixel_data[1] != 255) and (pixel_data[2] != 255) and (pixel_data[3] != 255)
                        )
                        or 
                        (
                            (pixel_data[1] != 0) and (pixel_data[2] != 0) and (pixel_data[3] != 0)
                        )
                )
                if(a):
                    area_counter = area_counter+1
        return area_counter

    def __calcMapCurves(self, feature:QgsRasterLayer, feature2:QgsRasterLayer):
        """Calculation MapCurve using feature.
        
        :param feature QgsFeature: The first feature
        :param feature2 QgsFeature: The second feature
        
        """
        # print(feature)
        # print(feature2)
        bb1 = QgsGeometry.fromRect(feature.extent())
        bb2 = QgsGeometry.fromRect(feature2.extent())
        # print(bb1)
        # print(bb2)
        bb_intersection = bb1.intersection(bb2)
        # print(bb_intersection)
        coord_bb = [ 
            bb_intersection.boundingBox().xMinimum(),
            bb_intersection.boundingBox().yMinimum(),
            bb_intersection.boundingBox().xMaximum(),
            bb_intersection.boundingBox().yMaximum()
        ]
        # print("Coordinates")
        # print("%1.2f - %1.2f - %1.2f - %1.2f" % (coord_bb[0],coord_bb[1],coord_bb[2],coord_bb[3]))
        coord_start = QgsPointXY(coord_bb[0], coord_bb[1])
        distances = [
            coord_start.distance(coord_bb[2],coord_bb[1]),
            coord_start.distance(coord_bb[0],coord_bb[3])
        ]
        # print("distances")
        # print(distances)
        # g_clone = feature.clone()
        # g2_clone = feature2.clone()
        r_ = (distances[0]/feature.rasterUnitsPerPixelX())
        r2_ = (distances[1]/feature2.rasterUnitsPerPixelY())
        # print("radius")
        # print(r_)
        # print(r2_)
        pixel_intersect_counter = 0
        progress_counter = 0
        area_counter = 0
        # print("rasterUnitsPerPixel")
        # print([
        #     coord_bb[0]+(feature.rasterUnitsPerPixelX()*1),
        #     coord_bb[1]+(feature.rasterUnitsPerPixelY()*1)
        # ])
        # print("range")
        # print(range(0, int(r_)))
        # print(range(0, int(r2_)))
        a = self.__getAreaRasterMap(feature)
        b = self.__getAreaRasterMap(feature2)
        print("Areas")
        print(a)
        print(b) 
        for i in range(0, int(r_)+1):
            for j in range(0, int(r2_)+1):
                # print(i)
                # print(j)
                p_ = QgsPointXY(
                        coord_bb[0]+(feature.rasterUnitsPerPixelX()*i),
                        coord_bb[1]+(feature.rasterUnitsPerPixelY()*j)
                    )
                # print(p_)
                pixel_data = feature.dataProvider().identify(
                    point = p_,
                    format = Qgis.RasterIdentifyFormat(1)
                ).results()
                pixel_data2 = feature2.dataProvider().identify(
                    point=p_,
                    format=Qgis.RasterIdentifyFormat(1)
                ).results()
                m = (
                    (
                        (pixel_data[1] == pixel_data2[1]) and (pixel_data[2] == pixel_data2[2]) and (pixel_data[3] == pixel_data2[3])
                    )
                    and 
                    (
                            ((pixel_data[1] != 255) and (pixel_data[2] != 255) and (pixel_data[3] != 255))
                        or 
                            ((pixel_data[1] != 0) and (pixel_data[2] != 0) and (pixel_data[3] != 0))
                    )
                )
                a_ = (
                        (
                            (pixel_data[1] != 255) and (pixel_data[2] != 255) and (pixel_data[3] != 255)
                        )
                        or 
                        (
                            (pixel_data[1] != 0) and (pixel_data[2] != 0) and (pixel_data[3] != 0)
                        )
                )
                # print("boolean condition")
                # print(m)
                # self.currentProgress.emit([m, pixel_data, pixel_data2])
                if m == True:
                    pixel_intersect_counter = pixel_intersect_counter+1
                # self.progressSim.emit([pixel_data, pixel_data2, m, pixel_intersect_counter])
                progress_counter = progress_counter+1
                # if(a_):
                #     area_counter = area_counter+1
                self.progress.emit(progress_counter/((int(r2_)+1)*int(r_)+1)*100)
        print("pixel_intersect_counter")
        print(pixel_intersect_counter)
        score = (float(pixel_intersect_counter)/float(a)) * (float(pixel_intersect_counter)/float(b)) *100
        self.finished.emit([score])
        return score
    
        # return score
            # print("calculated : "+str(self.cumulative)+" - "+str(score))
            # print("result emited")
    
    def run(self):
        """Run the object"""
        start = time.perf_counter()
        if self.killed is False :
            self.cumulative = 0
            self.similarLayer = []
            try:
                """Try to run"""
                self.eventTask.emit("Duplicating ....")
                try:
                    self.eventTask.emit("Calculating ....")
                    self.__calcMapCurves(self.layer, self.layer2)
                    self.eventTask.emit("Calculating Finished !!!!")
                except Exception as e:
                    self.error.emit("Error when calculating")
                    self.eventTask.emit("Error occured")
                    print(e)
            except:
                self.error.emit("Error when duplicating")
                self.eventTask.emit("Error Occured")
    def kill(self):
        """Set the killed status"""
        self.killed = True

    def alive(self):
        """Set the not to be killed"""
        self.killed = False

    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(float)
    progressSim = pyqtSignal(list)
    eventTask = pyqtSignal(str)
    currentProgress = pyqtSignal(list)