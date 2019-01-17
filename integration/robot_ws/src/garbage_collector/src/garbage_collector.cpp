#include <ros/ros.h>
#include <geometry_msgs/Twist.h>
#include <geometry_msgs/Point.h>
#include <nav_msgs/Odometry.h>
#include <tf/transform_datatypes.h>
#include <angles/angles.h>
#include <stdlib.h>
#include <stdio.h>
#include <image_transport/image_transport.h>
#include <cv_bridge/cv_bridge.h>
#include <sensor_msgs/image_encodings.h>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

ros::Publisher publisher;

// Compute centroid of the masked color.
cv::Point computeCentroid(const cv::Mat &mask) {
        cv::Moments m = moments(mask, true);
        cv::Point center(m.m10/m.m00, m.m01/m.m00);
        return center;
}

void cameraCallback(const sensor_msgs::ImageConstPtr& msg) {
        // Convert ros image to openCV image
        cv_bridge::CvImagePtr cv_image_ptr;
        try {
                cv_image_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
        }
        catch (cv_bridge::Exception& e)
        {
                ROS_ERROR("cv_bridge exception: %s", e.what());
                return;
        }

        // Convert bgr to hsv for different lighting conditions
        cv::Mat hsv;
        cv::cvtColor(cv_image_ptr->image, hsv, CV_BGR2HSV, 0);
        // Apply mask for red color
        // In HSV space, the red color wraps around 180. So we need the H values to be both in [0,10] and [170, 180].
        cv::Mat1b mask1, mask2;
        cv::inRange(hsv, cv::Scalar(0, 70, 50), cv::Scalar(10, 255, 255), mask1);
        cv::inRange(hsv, cv::Scalar(170, 70, 50), cv::Scalar(180, 255, 255), mask2);

        cv::Mat1b mask = mask1 | mask2;
        // Get centroids of the mask.
        cv::Point centroid = computeCentroid(mask);

        // Initialize the speeds to 0.
	geometry_msgs::Twist speed;
        speed.linear.y = speed.linear.x = speed.angular.z= 0.0;
        
        // If centroid for a red blob is not found, keep rotating the bot so that it continues to look for red color.
	if(centroid.x == INT_MIN && centroid.y == INT_MIN) {
		speed.angular.z = 0.1;
		speed.linear.y = speed.linear.x = 0.0;
	} else {
 	        // Centroid is found, i.e. a red blob is found
		if(centroid.x != INT_MIN && centroid.y > 650 ) { 
			// We are very close to the blob. Stop the blob.
			speed.linear.y = speed.linear.x = speed.angular.z= 0.0;
		} else {
			// We are able to see the blob. Move the bot towards the blob.
			speed.linear.y = speed.linear.z = 0.0;
                	speed.linear.x = 0.0;
		}
	}
        // Pubish the speed of the bot to cmd_vel
	publisher.publish(speed);
}

int main(int argc, char** argv) {
        // Initialize ROS node
        ros::init(argc, argv, "garbage_collector_bot");
        // Create node handler.
        ros::NodeHandle nodeHandle;
        // Create a subscriber to raw camera image.
        ros::Subscriber subscriber = nodeHandle.subscribe("/garbage_collector/camera/image_raw", 1000, cameraCallback);
        // Create a publisher to cmd_vel. This topic is used to update the velocity of the bot.
        publisher = nodeHandle.advertise<geometry_msgs::Twist>("cmd_vel", 1000);
        ros::Rate rate(2);
	ros::spin();
        return 0;
}

