Plugin Calculation Method
=============
.. toctree::
   :maxdepth: 2

calcMapCurvesGeom
------------------------------   
   calcMapCurvesGeom(self, g:QgsGeometry, g2:QgsGeometry)
      return int
         
         calculate the score in geometry

calcMapCurves
--------------------------------
   calcMapCurves(self, feature:QgsFeature, feature2:QgsFeature)
      return null
         
         calculate the socre and save to self.similarLayer

calcSq
-----------------------------
   calcSq(self, layer:QgsVectorLayer, layer2:QgsVectorLayer)
      return null
         
         calculate squentially

calcKNN
----------------------------------------------
   calcKNN(self, layer:QgsVectorLayer, layer2:QgsVectorLayer)
      return null
         
         Calculate within radius bounding box. Radius distance using euclidean

calcWK
----------------------------------------------
   calcWK(self, layer:QgsVectorLayer, layer2:QgsVectorLayer)
      return null
         
         Match the primary key map, see https://sig.bps.go.id/

translateCenterGeom
-----------------------------------------------
   translateCenterGeom(self, g:QgsGeometry, target:QgsGeometry)
      return QgsGeometry

         translate geometry