import cv2
import numpy as np

__all__ = ["TightBox"]

changed_poly = []


class TightBox:
    def __init__(self, root, cnv, thresh):
        self.root = root
        self.cnv = cnv
        self.thresh = thresh
        self.changed_poly = []

    def tight_box(self):
        _, polygons, _, _, _ = self.cnv.current_state()
        for p in polygons:
            if p.select_poly:
                cnt = []
                for pt in p.points:
                    cnt.append(p.get_pt_center(pt))
                self.changed_poly.append([p, cnt])
                cnt = np.array(cnt).reshape((-1, 1, 2)).astype(np.int32)

                # Load and preprocess the image
                img = cv2.imread(self.cnv.image_path)
                img = cv2.resize(img, self.cnv.img.size, interpolation=cv2.INTER_AREA)
                mask = np.zeros(img.shape[:2], np.uint8)
                cv2.fillPoly(mask, pts=[cnt], color=(255, 255, 255))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, img = cv2.threshold(img, self.thresh, 255, cv2.THRESH_BINARY)
                new_img = cv2.bitwise_and(img, img, mask=mask)

                # Find new contours in the masked image
                new_cnts, _ = cv2.findContours(new_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                new_cnts = sorted(new_cnts, key=cv2.contourArea, reverse=True)[1:]
                all_pts = [pt for ct in new_cnts for pt in ct]
                all_pts = np.array(all_pts).reshape((-1, 1, 2)).astype(np.int32)

                # Find the min-area rotated rectangle
                min_area_rect = cv2.minAreaRect(all_pts)
                box = cv2.boxPoints(min_area_rect)
                box = np.intp(box)

                # Get the center, width, height, and angle from the min-area rectangle
                center, size, angle = min_area_rect
                w, h = size

                # Expand by 2 pixels on each side (increase width and height)
                size = (w + 2, h + 2)

                # Use the expanded size to create the new rotated rectangle
                expanded_rect = cv2.boxPoints(((center[0], center[1]), size, angle))
                expanded_rect = np.intp(expanded_rect)

                # Update polygon points to match the expanded rotated rectangle
                for i, point in enumerate(p.points):
                    p.update_point(point, expanded_rect[i][0], expanded_rect[i][1])

                print(expanded_rect)
                p.update_polygon()
                p.draw_points()



    def save_tight_box(self):
        pass

    def discard_tight_box(self):
        for p, pts in self.changed_poly:
            for i, pt in enumerate(p.points):
                p.update_point(pt, pts[i][0], pts[i][1])
            p.update_polygon()
            p.draw_points()
        self.cnv.canvas.update()
