using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;

namespace SeerPng
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();

            GetFilesPath();

            OneStep();
        }

        public string[] files;
        public String ImgDir;
        public int index = 0;

        public void GetFilesPath()
        {
            ImgDir = @"D:\桌面\diyibanzhu\img - 副本";

            files = Directory.GetFiles(ImgDir, "*.png");

            //foreach (var file in files)
            //    Console.WriteLine(file);
        }

        public void OneStep()
        {
            String ImgPath = this.pictureBox1.ImageLocation;
            String ImgName = System.IO.Path.GetFileName(ImgPath);

            String DataFilePath = ImgDir + "\\" + "变形字体库v2.txt";
            String Line = this.textBox1.Text + " " + ImgName;
            //System.IO.File.WriteAllText(DataFilePath, Line, Encoding.UTF8);
            StreamWriter sw = File.AppendText(DataFilePath);
            sw.WriteLine(Line);
            sw.Close();


            // 下一张
            index++;
            this.textBox1.Text = "";
            this.pictureBox1.Load(files[index]);
        }
    }
}