from bs4 import BeautifulSoup
import re
import json

import re
from bs4 import BeautifulSoup

def parse_device_specs(html_content, parser='lxml'):
    # Use a faster parser if available (e.g., 'lxml')
    soup = BeautifulSoup(html_content, parser)
    result = []

    # Precompile regex to separate numbers and units
    value_pattern = re.compile(r"([\d.]+)\s*(.*)")

    # Use CSS selectors for clarity and performance
    for section in soup.select('header.section-header'):
        # Extract category and description using select_one and get_text
        category_tag = section.select_one('h2.header')
        category_desc_tag = section.select_one('h3.subheader')
        category = category_tag.get_text(strip=True) if category_tag else "Unknown Category"
        category_desc = category_desc_tag.get_text(strip=True) if category_desc_tag else "No Description"

        # Get the associated table; skip if not found
        table = section.find_next_sibling('table', class_='model-information-table')
        if not table:
            continue

        sub_categories = []
        for row in table.find_all('tr'):
            tds = row.find_all('td')
            if len(tds) != 2:
                continue

            # Extract sub-category text (direct child text only) and description
            sub_cat_text = tds[0].find(text=True, recursive=False)
            sub_category = sub_cat_text.strip() if sub_cat_text else "Unknown Sub-Category"
            sub_category_desc_tag = tds[0].find('p')
            sub_category_desc = sub_category_desc_tag.get_text(strip=True) if sub_category_desc_tag else ""

            values = []
            for content in tds[1].contents:
                # Skip <br> tags (or any tag with name 'br')
                if hasattr(content, 'name') and content.name == 'br':
                    continue

                if isinstance(content, str):
                    text = content.strip()
                    # Split by any newlines and clean up each part
                    parts = [s.strip() for s in text.split('\n') if s.strip()]
                    for part in parts:
                        match = value_pattern.match(part)
                        if match:
                            num, unit = match.groups()
                            values.append({
                                'value': num,
                                'unit': unit.strip('()') if unit else None
                            })
                        else:
                            values.append({'value': part, 'unit': None})

            sub_categories.append({
                'sub_category': sub_category,
                'sub_category_desc': sub_category_desc,
                'values': values
            })

        result.append({
            'category': category,
            'category_desc': category_desc,
            'sub_categories': sub_categories
        })

    return result


html_content = '''
<div style="width: 100%; margin-top: 20px;">
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/info.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Brand and model</h2>
        <h3 class="subheader">Information about the brand, model and model alias (if any) of a specific device.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Brand<p>Brand name of the company that manufactures the device.</p>
                </td>
                <td>Samsung</td>
            </tr>
            <tr>
                <td>Model<p>Model name of the device.</p>
                </td>
                <td>Galaxy S25 Ultra</td>
            </tr>
            <tr>
                <td>Model alias<p>Аlternative names, under which the model is known.</p>
                </td>
                <td><span class="&quot;arrow-bullet&quot;"></span>SM-S938B<br><span
                        class="&quot;arrow-bullet&quot;"></span>SM-S938B/DS<br><span
                        class="&quot;arrow-bullet&quot;"></span>SM-S938U<br><span
                        class="&quot;arrow-bullet&quot;"></span>SM-S938U1<br><span
                        class="&quot;arrow-bullet&quot;"></span>SM-S938W<br><span
                        class="&quot;arrow-bullet&quot;"></span>SM-S938N<br><span
                        class="&quot;arrow-bullet&quot;"></span>SM-S9380<br><span
                        class="&quot;arrow-bullet&quot;"></span>SM-S938E<br><span
                        class="&quot;arrow-bullet&quot;"></span>SM-S938E/DS</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/xyz.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Design</h2>
        <h3 class="subheader">Information about the dimensions and weight of the device, shown in different measurement
            units. Body materials, available colors, certifications.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Width<p>Information about the width, i.e. the horizontal side of the device when it is used in its
                        standard orientation.</p>
                </td>
                <td><span class="approximation-bullet"></span>77.6 mm <span>(millimeters)</span><br><span
                        class="approximation-bullet"></span>7.76 cm <span>(centimeters)</span><br><span
                        class="approximation-bullet"></span>0.255 ft <span>(feet)</span><br><span
                        class="approximation-bullet"></span>3.055 in <span>(inches)</span></td>
            </tr>
            <tr>
                <td>Height<p>Information about the height, i.e. the vertical side of the device when it is used in its
                        standard orientation.</p>
                </td>
                <td><span class="approximation-bullet"></span>162.8 mm <span>(millimeters)</span><br><span
                        class="approximation-bullet"></span>16.28 cm <span>(centimeters)</span><br><span
                        class="approximation-bullet"></span>0.534 ft <span>(feet)</span><br><span
                        class="approximation-bullet"></span>6.409 in <span>(inches)</span></td>
            </tr>
            <tr>
                <td>Thickness<p>Information about the thickness/depth of the device in different measurement units.</p>
                </td>
                <td><span class="approximation-bullet"></span>8.2 mm <span>(millimeters)</span><br><span
                        class="approximation-bullet"></span>0.82 cm <span>(centimeters)</span><br><span
                        class="approximation-bullet"></span>0.027 ft <span>(feet)</span><br><span
                        class="approximation-bullet"></span>0.323 in <span>(inches)</span></td>
            </tr>
            <tr>
                <td>Weight<p>Information about the weight of the device in different measurement units.</p>
                </td>
                <td><span class="approximation-bullet"></span>218 g <span>(grams)</span><br><span
                        class="approximation-bullet"></span>0.48 lbs <span>(pounds)</span><br><span
                        class="approximation-bullet"></span>7.69 oz <span>(ounces)</span></td>
            </tr>
            <tr>
                <td>Volume<p>Estimated volume of the device, calculated from the dimensions provided by the
                        manufacturer. Applies for devices in the form of a rectangular parallelepiped.</p>
                </td>
                <td><span class="approximation-bullet"></span>103.59 cm³ <span>(cubic centimeters)</span><br><span
                        class="approximation-bullet"></span>6.29 in³ <span>(cubic inches)</span></td>
            </tr>
            <tr>
                <td>Colors<p>Information about the colors, in which the device is available in the market.</p>
                </td>
                <td><span class="arrow-bullet"></span>Titanium Silverblue<br><span class="arrow-bullet"></span>Titanium
                    Black<br><span class="arrow-bullet"></span>Titanium Whitesilver<br><span
                        class="arrow-bullet"></span>Titanium Gray</td>
            </tr>
            <tr>
                <td>Body materials<p>Materials used in the fabrication of the device's body.</p>
                </td>
                <td><span class="arrow-bullet"></span>Glass<br><span class="arrow-bullet"></span>Armor Aluminum</td>
            </tr>
            <tr>
                <td>Certification<p>Information about the standards, in which the device is certified.</p>
                </td>
                <td><span class="arrow-bullet"></span>IP68</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/sim_card.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">SIM card</h2>
        <h3 class="subheader">The Subscriber Identity Module (SIM) is used in mobile devices for storing data
            authenticating the subscribers of mobile services.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>SIM card type<p>Information about the type and size (form factor) of the SIM card used in the
                        device.</p>
                </td>
                <td><span class="arrow-bullet"></span>Nano-SIM (4FF - fourth form factor, since 2012, 12.30 x 8.80 x
                    0.67 mm)<br><span class="arrow-bullet"></span>eSIM</td>
            </tr>
            <tr>
                <td>Number of SIM cards<p>Information about the number of SIM cards, supported by the device.</p>
                </td>
                <td>1</td>
            </tr>
            <tr>
                <td>Features<p>Information about some specific features related to the SIM card(s) of the device.</p>
                </td>
                <td><span class="arrow-bullet"></span>Dual SIM optional (A variant of the model with two SIM card slots
                    is available)</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/signal.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Networks</h2>
        <h3 class="subheader">A mobile (cellular) network is a radio system, which allows a large number of mobile
            devices to communicate with each other.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>GSM<p>GSM (Global System for Mobile Communications) was developed to replace the analog cellular
                        network (1G), therefore it is referred to as a 2G mobile network. It has been improved with the
                        addition of General Packet Radio Services (GPRS) and later via the Enhanced Data rates for GSM
                        Evolution (EDGE) technology.</p>
                </td>
                <td><span class="arrow-bullet"></span>GSM 850 MHz (B5)<br><span class="arrow-bullet"></span>GSM 900 MHz
                    (B8)<br><span class="arrow-bullet"></span>GSM 1800 MHz (B3)<br><span class="arrow-bullet"></span>GSM
                    1900 MHz (B2)</td>
            </tr>
            <tr>
                <td>UMTS<p>UMTS stands for Universal Mobile Telecommunications System. Based on the GSM standard, it is
                        deemed as a 3G mobile network standard. It has been developed by the 3GPP and its major
                        advantage is the provision of greater bandwidth and spectral efficiency, due to the W-CDMA
                        technology.</p>
                </td>
                <td><span class="arrow-bullet"></span>UMTS 850 MHz (B5)<br><span class="arrow-bullet"></span>UMTS 900
                    MHz (B8)<br><span class="arrow-bullet"></span>UMTS 1700 MHz (B4)<br><span
                        class="arrow-bullet"></span>UMTS 1900 MHz (B2)<br><span class="arrow-bullet"></span>UMTS 2100
                    MHz (B1)</td>
            </tr>
            <tr>
                <td>LTE<p>LTE is deemed to be the fourth generation (4G) of mobile communications technology. It has
                        been developed by the 3GPP based on the GSM/EDGE and UMTS/HSPA technologies in order to increase
                        the speed and capacity of wireless data networks. A further development of the technology is
                        called LTE Advanced.</p>
                </td>
                <td><span class="arrow-bullet"></span>LTE-FDD 700 MHz (B12)<br><span class="arrow-bullet"></span>LTE-FDD
                    700 MHz (B13)<br><span class="arrow-bullet"></span>LTE-FDD 700 MHz (B17)<br><span
                        class="arrow-bullet"></span>LTE-FDD 700 MHz (B28)<br><span class="arrow-bullet"></span>LTE-FDD
                    800 MHz (B20)<br><span class="arrow-bullet"></span>LTE-FDD 850 MHz (B5)<br><span
                        class="arrow-bullet"></span>LTE-FDD 900 MHz (B8)<br><span class="arrow-bullet"></span>LTE-FDD
                    1700 MHz (B4)<br><span class="arrow-bullet"></span>LTE-FDD 1800 MHz (B3)<br><span
                        class="arrow-bullet"></span>LTE-FDD 1900 MHz (B2)<br><span class="arrow-bullet"></span>LTE-FDD
                    2100 MHz (B1)<br><span class="arrow-bullet"></span>LTE-FDD 2600 MHz (B7)<br><span
                        class="arrow-bullet"></span>LTE-TDD 1900 MHz (B39)<br><span class="arrow-bullet"></span>LTE-TDD
                    2000 MHz (B34)<br><span class="arrow-bullet"></span>LTE-TDD 2300 MHz (B40)<br><span
                        class="arrow-bullet"></span>LTE-TDD 2500 MHz (B41)<br><span class="arrow-bullet"></span>LTE-TDD
                    2600 MHz (B38)</td>
            </tr>
            <tr>
                <td>5G NR<p>The 5G (fifth generation) mobile networks use the new radio access technology (RAT)
                        developed by 3GPP, dubbed 5G NR and deemed as the global standard for the air interface of 5G
                        networks. 5G NR operates in two frequency ranges - FR1 (sub-6 GHz) and FR2 (above 24 GHz). In
                        the FR1 frequency range, the 5G mobile networks use a number of bands, some of which are
                        traditionally used by previous standards. The FR2 provides shorter range but higher available
                        bandwidth than bands in the FR1.</p>
                </td>
                <td><span class="arrow-bullet"></span>5G-FDD 700 MHz (n28)<br><span class="arrow-bullet"></span>5G-FDD
                    850 MHz (n5)<br><span class="arrow-bullet"></span>5G-FDD 900 MHz (n8)<br><span
                        class="arrow-bullet"></span>5G-FDD 1800 MHz (n3)<br><span class="arrow-bullet"></span>5G-FDD
                    2100 MHz (n1)<br><span class="arrow-bullet"></span>5G-TDD 2300 MHz (n40)<br><span
                        class="arrow-bullet"></span>5G-FDD 2600 MHz (n7)<br><span class="arrow-bullet"></span>5G-TDD
                    3500 MHz (n78)<br><span class="arrow-bullet"></span>5G-TDD 3700 MHz (n77)</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/up_down.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Mobile network technologies and bandwidth</h2>
        <h3 class="subheader">Communication between devices within mobile networks is realized via various generations
            of network technologies, which provide different bandwidth.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Mobile network technologies<p>There are several network technologies that enhance the performance of
                        mobile networks mainly by increased data bandwidth. Information about the communication
                        technologies supported by the device and their respective uplink and downlink bandwidth.</p>
                </td>
                <td><span class="arrow-bullet"></span>UMTS (384 kbit/s <span class="arrow-down"></span>)<br><span
                        class="arrow-bullet"></span>EDGE<br><span class="arrow-bullet"></span>GPRS<br><span
                        class="arrow-bullet"></span>HSPA+<br><span class="arrow-bullet"></span>LTE<br><span
                        class="arrow-bullet"></span>5G SA<br><span class="arrow-bullet"></span>5G NSA</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/gear.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Operating system</h2>
        <h3 class="subheader">Operating system is the system software, which manages and controls the functioning of the
            hardware components of the device.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Operating system (OS)<p>Information about the operating system used by the device as well as its
                        version.</p>
                </td>
                <td><span class="arrow-bullet"></span>Android 15</td>
            </tr>
            <tr>
                <td>User interface (UI)<p>Name and version of the user interface (UI) used by the operating system (OS).
                    </p>
                </td>
                <td><span class="arrow-bullet"></span>One UI 7.0</td>
            </tr>
        </tbody>
    </table>
    <div style="margin-top: 40px; padding: 20px 0px 20px 0px;">
        <script async="" src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
        <!-- DS - Responsive -->
        <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-5326452196367087"
            data-ad-slot="4450651738" data-ad-format="auto" data-full-width-responsive="true"
            data-adsbygoogle-status="done"><iframe id="aswift_1"
                style="height: 1px !important; max-height: 1px !important; max-width: 1px !important; width: 1px !important;"><iframe
                    id="google_ads_frame1"></iframe></iframe></ins>
        <script>
            (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
    </div>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/soc.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">System on Chip (SoC)</h2>
        <h3 class="subheader">A system on a chip (SoC) includes into a single chip some of the main hardware components
            of the mobile device.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>SoC<p>The SoC integrates different hardware components such as the CPU, GPU, memory, peripherals,
                        interfaces, etc., as well as software for their functioning.</p>
                </td>
                <td>Qualcomm Snapdragon 8 Elite for Galaxy (SM8750-AC)</td>
            </tr>
            <tr>
                <td>Process technology<p>Information about the process technology used in manufacturing the chip. The
                        value in nanometers represents half the distance between elements that make up the CPU.</p>
                </td>
                <td>3 nm <span>(nanometers)</span></td>
            </tr>
            <tr>
                <td>CPU<p>CPU is the Central Processing Unit or the processor of a mobile device. Its main function is
                        to interpret and execute instructions contained in software applications.</p>
                </td>
                <td>2x 4.47 GHz, 6x 3.53 GHz</td>
            </tr>
            <tr>
                <td>CPU bits<p>The CPU bits are determined by the bit-size of the processor registers, address buses and
                        data buses. 64-bit CPUs provide better performance than 32-bit ones, which on their part perform
                        better than 16-bit processors.</p>
                </td>
                <td>64 bit</td>
            </tr>
            <tr>
                <td>Instruction set<p>The instruction set architecture (ISA) is a set of commands used by the software
                        to manage the CPU's work. Information about the set of instructions the processor can execute.
                    </p>
                </td>
                <td>ARMv9.2-A</td>
            </tr>
            <tr>
                <td>Level 2 cache memory (L2)<p>The L2 (level 2) cache memory is slower than L1, but has a larger
                        capacity, instead, which allows it to cache more data. Just like L1, it is much faster than the
                        system memory (RAM). If the CPU does not find the data needed in L2, it proceeds to look for
                        them in the L3 cache memory (if there is such) or in the RAM.</p>
                </td>
                <td>2400 KB <span>(kilobytes)</span><br>2.34375 MB <span>(megabytes)</span></td>
            </tr>
            <tr>
                <td>CPU cores<p>A CPU core is the processor unit, which executes software instructions. Presently,
                        besides single-core processors, there are dual-core, quad-core, hexa-core and so on multi-core
                        processors. They increase the performance of the device allowing the execution of multiple
                        instructions in parallel.</p>
                </td>
                <td>8</td>
            </tr>
            <tr>
                <td>CPU frequency<p>The frequency of the processor describes its clock rate in cycles per second. It is
                        measured in Megahertz (MHz) or Gigahertz (GHz).</p>
                </td>
                <td>4470 MHz <span>(megahertz)</span></td>
            </tr>
            <tr>
                <td>GPU<p>GPU is a graphical processing unit, which handles computation for 2D/3D graphics applications.
                        In mobile devices GPU is usually utilized by games, UI, video playback, etc. GPU can also
                        perform computation in applications traditionally handled by the CPU.</p>
                </td>
                <td>Qualcomm Adreno 830</td>
            </tr>
            <tr>
                <td>GPU frequency<p>The frequency is the clock rate of the graphic processor (GPU), which is measured in
                        Megahertz (MHz) or Gigahertz (GHz).</p>
                </td>
                <td>1200 MHz <span>(megahertz)</span></td>
            </tr>
            <tr>
                <td>RAM capacity<p>RAM (Random-Access Memory) is used by the operating system and all installed
                        applications. Data in the RAM is lost after the device is turned off or restarted.</p>
                </td>
                <td><span class="arrow-bullet"></span>12 GB <span>(gigabytes)</span><br><span
                        class="arrow-bullet"></span>16 GB <span>(gigabytes)</span></td>
            </tr>
            <tr>
                <td>RAM type<p>Information about the type of RAM used by the device.</p>
                </td>
                <td>LPDDR5X</td>
            </tr>
            <tr>
                <td>RAM channels<p>Information about the number of RAM channels integrated in the SoC. More channels
                        mean higher data transfer rates.</p>
                </td>
                <td>Quad channel</td>
            </tr>
            <tr>
                <td>RAM frequency<p>RAM frequency relates directly to the rate of reading/writing from/in the RAM
                        memory.</p>
                </td>
                <td>4800 MHz <span>(megahertz)</span></td>
            </tr>
            <tr>
                <td></td>
                <td><span class="arrow-bullet"></span>Snapdragon Cognitive ISP with Semantic Segmentation</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/storage.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Storage</h2>
        <h3 class="subheader">Every mobile device has a built-in storage (internal memory) with a fixed capacity.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Storage<p>Information about the capacity of the built-in storage of the device. Sometimes one and
                        the same model may is offered in variants with different internal storage capacity.</p>
                </td>
                <td><span class="arrow-bullet"></span>256 GB <span>(gigabytes)</span><br><span
                        class="arrow-bullet"></span>512 GB <span>(gigabytes)</span><br><span
                        class="arrow-bullet"></span>1024 GB <span>(gigabytes)</span></td>
            </tr>
            <tr>
                <td></td>
                <td><span class="arrow-bullet"></span>UFS 4.0</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/display.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Display</h2>
        <h3 class="subheader">The display of a mobile device is characterized by its technology, resolution, pixel
            density, diagonal length, color depth, etc.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Type/technology<p>One of the main characteristics of the display is its type/technology, on which
                        depends its performance.</p>
                </td>
                <td>Dynamic AMOLED 2X</td>
            </tr>
            <tr>
                <td>Diagonal size<p>In mobile devices display size is represented by the length of its diagonal measured
                        in inches.</p>
                </td>
                <td><span class="approximation-bullet"></span>6.8 in <span>(inches)</span><br><span
                        class="approximation-bullet"></span>172.72 mm <span>(millimeters)</span><br><span
                        class="approximation-bullet"></span>17.27 cm <span>(centimeters)</span></td>
            </tr>
            <tr>
                <td>Width<p>Approximate width of the display</p>
                </td>
                <td><span class="approximation-bullet"></span>2.85 in <span>(inches)</span><br><span
                        class="approximation-bullet"></span>72.38 mm <span>(millimeters)</span><br><span
                        class="approximation-bullet"></span>7.24 cm <span>(centimeters)</span></td>
            </tr>
            <tr>
                <td>Height<p>Approximate height of the display</p>
                </td>
                <td><span class="approximation-bullet"></span>6.17 in <span>(inches)</span><br><span
                        class="approximation-bullet"></span>156.82 mm <span>(millimeters)</span><br><span
                        class="approximation-bullet"></span>15.68 cm <span>(centimeters)</span></td>
            </tr>
            <tr>
                <td>Aspect ratio<p>The ratio between the long and the short side of the display</p>
                </td>
                <td><span class="approximation-bullet"></span>2.167:1</td>
            </tr>
            <tr>
                <td>Resolution<p>The display resolution shows the number of pixels on the horizontal and vertical side
                        of the screen. The higher the resolution is, the greater the detail of the displayed content.
                    </p>
                </td>
                <td>1440 x 3120 pixels</td>
            </tr>
            <tr>
                <td>Pixel density<p>Information about the number of pixels per centimeter (ppcm) or per inch (ppi) of
                        the display. The higher the pixel density, the more detailed and clearer is the information
                        displayed on the screen.</p>
                </td>
                <td><span class="approximation-bullet"></span>505 ppi <span>(pixels per inch)</span><br><span
                        class="approximation-bullet"></span>198 ppcm <span>(pixels per centimeter)</span></td>
            </tr>
            <tr>
                <td>Color depth<p>The color depth of the display is also known as bit depth. It shows the number of bits
                        used for the color components of one pixel. Information about the maximum number of colors the
                        screen can display.</p>
                </td>
                <td>24 bit<br>16777216 colors</td>
            </tr>
            <tr>
                <td>Display area<p>The estimated percentage of the screen area from the device's front area.</p>
                </td>
                <td><span class="approximation-bullet"></span>90.14 % <span>(percent)</span></td>
            </tr>
            <tr>
                <td>Other features<p>Information about other functions and features of the display.</p>
                </td>
                <td><span class="arrow-bullet"></span>Capacitive<br><span
                        class="arrow-bullet"></span>Multi-touch<br><span class="arrow-bullet"></span>Scratch resistant
                </td>
            </tr>
            <tr>
                <td></td>
                <td><span class="arrow-bullet"></span>Corning Gorilla Armor 2<br><span
                        class="arrow-bullet"></span>Infinity-O Display<br><span class="arrow-bullet"></span>Always-On
                    Display<br><span class="arrow-bullet"></span>LTPO<br><span class="arrow-bullet"></span>2600 cd/m²
                    peak brightness<br><span class="arrow-bullet"></span>1-120 Hz refresh rate<br><span
                        class="arrow-bullet"></span>VRR<br><span class="arrow-bullet"></span>HDR10+<br><span
                        class="arrow-bullet"></span>Vision Booster technology</td>
            </tr>
        </tbody>
    </table>
    <div style="margin-top: 40px; padding: 20px 0px 20px 0px;">
        <script async="" src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
        <!-- DS - Responsive -->
        <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-5326452196367087"
            data-ad-slot="4450651738" data-ad-format="auto" data-full-width-responsive="true"
            data-adsbygoogle-status="done"><iframe id="aswift_2"
                style="height: 1px !important; max-height: 1px !important; max-width: 1px !important; width: 1px !important;"><iframe
                    id="google_ads_frame2"></iframe></iframe></ins>
        <script>
            (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
    </div>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/gauge.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Sensors</h2>
        <h3 class="subheader">Different sensors measure different physical quantities and convert them into signals
            recognizable by the mobile device.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Sensors<p>Sensors vary in type and purpose. They increase the overall functionality of the device,
                        in which they are integrated.</p>
                </td>
                <td><span class="arrow-bullet"></span>Proximity<br><span class="arrow-bullet"></span>Light<br><span
                        class="arrow-bullet"></span>Accelerometer<br><span class="arrow-bullet"></span>Compass<br><span
                        class="arrow-bullet"></span>Gyroscope<br><span class="arrow-bullet"></span>Barometer<br><span
                        class="arrow-bullet"></span>Geomagnetic<br><span
                        class="arrow-bullet"></span>Fingerprint<br><span class="arrow-bullet"></span>Hall<br><span
                        class="arrow-bullet"></span>Gravity</td>
            </tr>
            <tr>
                <td></td>
                <td><span class="arrow-bullet"></span>In-display ultrasonic fingerprint sensor</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/camera_1.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Rear camera</h2>
        <h3 class="subheader">The primary camera of the mobile device is usually placed on its back and can be combined
            with one or more additional cameras.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Sensor model<p>Information about the manufacturer and model of the image sensor used by this camera
                        of the device.</p>
                </td>
                <td>Samsung</td>
            </tr>
            <tr>
                <td>Sensor type<p>Information about the sensor type of the camera. Some of the most widely used types of
                        image sensors on mobile devices are CMOS, BSI, ISOCELL, etc.</p>
                </td>
                <td>ISOCELL</td>
            </tr>
            <tr>
                <td>Sensor format<p>The optical format of an image sensor is an indication of its shape and size. It is
                        usually expressed in inches.</p>
                </td>
                <td>1/1.3"</td>
            </tr>
            <tr>
                <td>Pixel size<p>Pixels are usually measured in microns (μm). Larger ones are capable of recording more
                        light, hence, will offer better low light shooting and wider dynamic range compared to the
                        smaller pixels. On the other hand, smaller pixels allow for increasing the resolution while
                        preserving the same sensor size.</p>
                </td>
                <td><span class="approximation-bullet"></span>0.6 µm <span>(micrometers)</span><br><span
                        class="approximation-bullet"></span>0.000600 mm <span>(millimeters)</span></td>
            </tr>
            <tr>
                <td>Aperture<p>The aperture (f-stop number) indicates the size of the lens diaphragm opening, which
                        controls the amount of light reaching the image sensor. The lower the f-stop number, the larger
                        the diaphragm opening is, hence, the more light reaches the sensor. Usually, the f-stop number
                        specified is the one that corresponds to the maximum possible diaphragm opening.</p>
                </td>
                <td>f/1.7</td>
            </tr>
            <tr>
                <td>Focal length and 35 mm equivalent<p>Focal length is the distance in millimeters from the focal point
                        of the image sensor to the optical center of the lens. The 35 mm equivalent indicates the focal
                        length at which a full-frame camera will achieve an angle of view that's the same as the one of
                        the camera of the mobile device. It is measured by multiplying the native focal length of the
                        camera by the crop factor of the sensor. The crop factor itself can be determined as the ratio
                        between the diagonal distances of the image sensor in the 35 mm camera and a given sensor.</p>
                </td>
                <td><span class="approximation-bullet"></span>6.3 mm <span>(millimeters)</span><br><span
                        class="approximation-bullet"></span>24 mm <span>(millimeters)</span> <sup>*(35 mm / full
                        frame)</sup></td>
            </tr>
            <tr>
                <td>Field of view<p>In photography, the Field of view (FoV) depends not only on the focal length of the
                        lens but also on the sensor size. It is derived from the lens's angle of view and the sensor's
                        crop factor. The lens's angle of view is a measure of the angle between the two farthest
                        separated points within the frame measured diagonally. Simply put, this is how much of a scene
                        in front of the camera will be captured by the camera's sensor. </p>
                </td>
                <td>85 ° <span>(degrees)</span></td>
            </tr>
            <tr>
                <td>Flash type<p>The rear cameras of mobile devices use mainly a LED flash. It may arrive in a single,
                        dual- or multi-light setup and in different arrangements.</p>
                </td>
                <td>LED</td>
            </tr>
            <tr>
                <td>Image resolution<p>One of the main characteristics of the cameras is their image resolution. It
                        states the number of pixels on the horizontal and vertical dimensions of the image, which can
                        also be shown in megapixels that indicate the approximate number of pixels in millions.</p>
                </td>
                <td>200 MP <span>(megapixels)</span></td>
            </tr>
            <tr>
                <td>Video resolution<p>Information about the maximum resolution at which the rear camera can shoot
                        videos.</p>
                </td>
                <td>7680 x 4320 pixels<br>33.18 MP <span>(megapixels)</span></td>
            </tr>
            <tr>
                <td>Video FPS<p>Information about the maximum number of frames per second (fps) supported by the rear
                        camera while recording video at the maximum resolution. Some of the main standard frame rates
                        for recording and playing video are 24 fps, 25 fps, 30 fps, 60 fps.</p>
                </td>
                <td>30 fps <span>(frames per second)</span></td>
            </tr>
            <tr>
                <td>Features<p>Information about additional software and hardware features of the rear camera which
                        improve its overall performance.</p>
                </td>
                <td><span class="arrow-bullet"></span>Autofocus<br><span class="arrow-bullet"></span>Continuous
                    autofocus<br><span class="arrow-bullet"></span>Continuous shooting<br><span
                        class="arrow-bullet"></span>Digital zoom<br><span class="arrow-bullet"></span>Optical
                    zoom<br><span class="arrow-bullet"></span>Digital image stabilization<br><span
                        class="arrow-bullet"></span>Optical image stabilization<br><span
                        class="arrow-bullet"></span>Geotagging<br><span class="arrow-bullet"></span>Panorama<br><span
                        class="arrow-bullet"></span>HDR<br><span class="arrow-bullet"></span>Touch focus<br><span
                        class="arrow-bullet"></span>Face detection<br><span class="arrow-bullet"></span>White balance
                    settings<br><span class="arrow-bullet"></span>ISO settings<br><span
                        class="arrow-bullet"></span>Exposure compensation<br><span
                        class="arrow-bullet"></span>Self-timer<br><span class="arrow-bullet"></span>Scene mode<br><span
                        class="arrow-bullet"></span>Macro mode<br><span class="arrow-bullet"></span>Phase detection
                    autofocus (PDAF)<br><span class="arrow-bullet"></span>Laser autofocus (LAF)<br><span
                        class="arrow-bullet"></span>Expert RAW<br><span class="arrow-bullet"></span>Astro
                    Hyperlapse<br><span class="arrow-bullet"></span>Adaptive VDIS<br><span
                        class="arrow-bullet"></span>Zoom Anyplace</td>
            </tr>
            <tr>
                <td></td>
                <td><span class="arrow-bullet"></span>12 MP photos with 16-in-1 pixel binning<br><span
                        class="arrow-bullet"></span>50 MP photos with 4-in-1 pixel binning<br><span
                        class="arrow-bullet"></span>Phase detection autofocus<br><span class="arrow-bullet"></span>Super
                    Quad Pixel autofocus<br><span class="arrow-bullet"></span>Object tracking AF<br><span
                        class="arrow-bullet"></span>Dual OIS<br><span class="arrow-bullet"></span>HDR10+ video
                    recording<br><span class="arrow-bullet"></span>4K Super HDR @ 60 fps<br><span
                        class="arrow-bullet"></span>Secondary rear camera - 50 MP (ultra-wide)<br><span
                        class="arrow-bullet"></span>Pixel size - 0.7 μm (#2)<br><span
                        class="arrow-bullet"></span>Aperture size - f/1.9 (#2)<br><span
                        class="arrow-bullet"></span>Angle of view - 120° (#2)<br><span class="arrow-bullet"></span>Focal
                    length (35 mm equivalent) - 13 mm (#2)<br><span class="arrow-bullet"></span>Phase detection with
                    Dual Pixel (#2)<br><span class="arrow-bullet"></span>Third rear camera - 50 MP (telephoto)<br><span
                        class="arrow-bullet"></span>Sensor model - Sony IMX875 (#3)<br><span
                        class="arrow-bullet"></span>Sensor size - 1/2.52" (#3)<br><span
                        class="arrow-bullet"></span>Pixel size - 0.7 μm (#3)<br><span
                        class="arrow-bullet"></span>Aperture size - f/3.4 (#3)<br><span
                        class="arrow-bullet"></span>Focal length (35 mm equivalent) - 111 mm (#3)<br><span
                        class="arrow-bullet"></span>Angle of view - 22° (#3)<br><span class="arrow-bullet"></span>5x
                    optical zoom (#3)<br><span class="arrow-bullet"></span>OIS (#3)<br><span
                        class="arrow-bullet"></span>Phase detection with Dual Pixel (#3)<br><span
                        class="arrow-bullet"></span>Fourth rear camera - 10 MP (telephoto)<br><span
                        class="arrow-bullet"></span>Sensor model - Sony (#4)<br><span class="arrow-bullet"></span>Sensor
                    size - 1/3.52" (#4)<br><span class="arrow-bullet"></span>Pixel size - 1.12 μm (#4)<br><span
                        class="arrow-bullet"></span>Aperture size - f/2.4 (#4)<br><span
                        class="arrow-bullet"></span>Angle of view - 36° (#4)<br><span class="arrow-bullet"></span>Focal
                    length (35 mm equivalent) - 69 mm (#4)<br><span class="arrow-bullet"></span>3x optical zoom
                    (#4)<br><span class="arrow-bullet"></span>OIS (#4)<br><span class="arrow-bullet"></span>Phase
                    detection with Dual Pixel (#4)</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/camera_2.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Front camera</h2>
        <h3 class="subheader">Modern smartphones have one or more front cameras and their positioning has led to various
            design concepts – pop-up camera, rotating camera, notch, punch hole, under-display camera, etc.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Sensor type<p>Information about the sensor type of the camera. Some of the most widely used types of
                        image sensors on mobile devices are CMOS, BSI, ISOCELL, etc.</p>
                </td>
                <td>CMOS (complementary metal-oxide semiconductor)</td>
            </tr>
            <tr>
                <td>Sensor format<p>The optical format of an image sensor is an indication of its shape and size. It is
                        usually expressed in inches.</p>
                </td>
                <td>1/2.82"</td>
            </tr>
            <tr>
                <td>Pixel size<p>Pixels are usually measured in microns (μm). Larger ones are capable of recording more
                        light, hence, will offer better low light shooting and wider dynamic range compared to the
                        smaller pixels. On the other hand, smaller pixels allow for increasing the resolution while
                        preserving the same sensor size.</p>
                </td>
                <td><span class="approximation-bullet"></span>0.7 µm <span>(micrometers)</span><br><span
                        class="approximation-bullet"></span>0.000700 mm <span>(millimeters)</span></td>
            </tr>
            <tr>
                <td>Aperture<p>The aperture (f-stop number) indicates the size of the lens diaphragm opening, which
                        controls the amount of light reaching the image sensor. The lower the f-stop number, the larger
                        the diaphragm opening is, hence, the more light reaches the sensor. Usually, the f-stop number
                        specified is the one that corresponds to the maximum possible diaphragm opening.</p>
                </td>
                <td>f/2.2</td>
            </tr>
            <tr>
                <td>Focal length and 35 mm equivalent<p>Focal length is the distance in millimeters from the focal point
                        of the image sensor to the optical center of the lens. The 35 mm equivalent indicates the focal
                        length at which a full-frame camera will achieve an angle of view that's the same as the one of
                        the camera of the mobile device. It is measured by multiplying the native focal length of the
                        camera by the crop factor of the sensor. The crop factor itself can be determined as the ratio
                        between the diagonal distances of the image sensor in the 35 mm camera and a given sensor.</p>
                </td>
                <td><span class="approximation-bullet"></span>26 mm <span>(millimeters)</span> <sup>*(35 mm / full
                        frame)</sup></td>
            </tr>
            <tr>
                <td>Field of view<p>In photography, the Field of view (FoV) depends not only on the focal length of the
                        lens but also on the sensor size. It is derived from the lens's angle of view and the sensor's
                        crop factor. The lens's angle of view is a measure of the angle between the two farthest
                        separated points within the frame measured diagonally. Simply put, this is how much of a scene
                        in front of the camera will be captured by the camera's sensor.</p>
                </td>
                <td>80 ° <span>(degrees)</span></td>
            </tr>
            <tr>
                <td>Image resolution<p>Information about the number of pixels on the horizontal and vertical dimensions
                        of the photos taken by the front camera, indicated in megapixels as well.</p>
                </td>
                <td>12 MP <span>(megapixels)</span></td>
            </tr>
            <tr>
                <td>Video resolution<p>Information about the maximum resolution of the videos shot by the front camera.
                    </p>
                </td>
                <td>3840 x 2160 pixels<br>8.29 MP <span>(megapixels)</span></td>
            </tr>
            <tr>
                <td>Video FPS<p>Digital cameras are able to shoot videos at different frames per second (fps). Some of
                        the main standard frame rates for recording and playing video are 24 fps, 25 fps, 30 fps, 60
                        fps. Information about the maximum possible fps for shooting videos at the maximum possible
                        resolution.</p>
                </td>
                <td>60 fps <span>(frames per second)</span></td>
            </tr>
            <tr>
                <td>Features<p>Information about additional software and hardware features of the front camera which
                        improve its overall performance.</p>
                </td>
                <td><span class="arrow-bullet"></span>Phase detection autofocus (PDAF)<br><span
                        class="arrow-bullet"></span>HDR<br><span class="arrow-bullet"></span>Autofocus</td>
            </tr>
            <tr>
                <td></td>
                <td><span class="arrow-bullet"></span>Phase detection with Dual Pixel<br><span
                        class="arrow-bullet"></span>Auto HDR</td>
            </tr>
        </tbody>
    </table>
    <div style="margin-top: 40px; padding: 20px 0px 20px 0px;">
        <script async="" src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
        <!-- DS - Responsive -->
        <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-5326452196367087"
            data-ad-slot="4450651738" data-ad-format="auto" data-full-width-responsive="true"
            data-adsbygoogle-status="done"><iframe id="aswift_3"
                style="height: 1px !important; max-height: 1px !important; max-width: 1px !important; width: 1px !important;"><iframe
                    id="google_ads_frame3"></iframe></iframe></ins>
        <script>
            (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
    </div>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/speaker.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Audio</h2>
        <h3 class="subheader">Information about the type of speakers and the audio technologies supported by the device.
        </h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Speaker<p>The loudspeaker is a device, which reproduces various sounds such as ring tones, alarms,
                        music, voice calls, etc. Information about the type of speakers the device uses.</p>
                </td>
                <td><span class="arrow-bullet"></span>Loudspeaker<br><span class="arrow-bullet"></span>Earpiece<br><span
                        class="arrow-bullet"></span>Stereo speakers</td>
            </tr>
            <tr>
                <td></td>
                <td><span class="arrow-bullet"></span>384 kHz / 32-bit<br><span class="arrow-bullet"></span>AKG
                    audio<br><span class="arrow-bullet"></span>Dolby Atmos</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/radio.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Radio</h2>
        <h3 class="subheader">The radio in a mobile device is a built-in FM radio receiver.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Radio<p>Information whether the device has an FM radio receiver or not.</p>
                </td>
                <td>Yes</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/positioning.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Tracking/Positioning</h2>
        <h3 class="subheader">Information about the positioning and navigation technologies supported by the device.
        </h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Tracking/Positioning<p>The tracking/positioning service is provided by various satellite navigation
                        systems, which track the autonomous geo-spatial positioning of the device that supports them.
                        The most common satellite navigation systems are the GPS and the GLONASS. There are also
                        non-satellite technologies for locating mobile devices such as the Enhanced Observed Time
                        Difference, Enhanced 911, GSM Cell ID.</p>
                </td>
                <td><span class="arrow-bullet"></span>GPS<br><span class="arrow-bullet"></span>A-GPS<br><span
                        class="arrow-bullet"></span>GLONASS<br><span class="arrow-bullet"></span>BeiDou<br><span
                        class="arrow-bullet"></span>Galileo<br><span class="arrow-bullet"></span>QZSS</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/wifi.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Wi-Fi</h2>
        <h3 class="subheader">Wi-Fi is a technology that provides wireless data connections between various devices
            within a short range.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Wi-Fi<p>Wi-Fi communication between devices is realized via the IEEE 802.11 standards. Some devices
                        have the possibility to serve as Wi-Fi Hotspots by providing internet access for other nearby
                        devices. Wi-Fi Direct (Wi-Fi P2P) is another useful standard that allows devices to communicate
                        with each other without the need for wireless access point (WAP).</p>
                </td>
                <td><span class="arrow-bullet"></span>802.11a (IEEE 802.11a-1999)<br><span
                        class="arrow-bullet"></span>802.11b (IEEE 802.11b-1999)<br><span
                        class="arrow-bullet"></span>802.11g (IEEE 802.11g-2003)<br><span
                        class="arrow-bullet"></span>802.11n (IEEE 802.11n-2009)<br><span
                        class="arrow-bullet"></span>802.11n 5GHz<br><span class="arrow-bullet"></span>802.11ac (IEEE
                    802.11ac)<br><span class="arrow-bullet"></span>Wi-Fi 6 (IEEE 802.11ax)<br><span
                        class="arrow-bullet"></span>Wi-Fi 7 (IEEE 802.11be)<br><span class="arrow-bullet"></span>Wi-Fi
                    Hotspot<br><span class="arrow-bullet"></span>Wi-Fi Direct<br><span class="arrow-bullet"></span>Wi-Fi
                    Display</td>
            </tr>
            <tr>
                <td></td>
                <td><span class="arrow-bullet"></span>HE80<br><span class="arrow-bullet"></span>MiMO<br><span
                        class="arrow-bullet"></span>1024-QAM</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/bluetooth.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Bluetooth</h2>
        <h3 class="subheader">Bluetooth is a standard for secure wireless data transfer between different types of
            devices over short distances.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Version<p>The technology has several versions, which improve the connection speed, range,
                        connectivity and discoverability of the devices. Information about the Bluetooth version of the
                        device.</p>
                </td>
                <td>5.4</td>
            </tr>
            <tr>
                <td>Features<p>Bluetooth uses various profiles and protocols related to faster exchange of data, energy
                        saving, better device discoverability, etc. Some of those supported by the device are listed
                        here.</p>
                </td>
                <td><span class="arrow-bullet"></span>A2DP (Advanced Audio Distribution Profile)<br><span
                        class="arrow-bullet"></span>AVRCP (Audio/Visual Remote Control Profile)<br><span
                        class="arrow-bullet"></span>DIP (Device ID Profile)<br><span class="arrow-bullet"></span>HFP
                    (Hands-Free Profile)<br><span class="arrow-bullet"></span>HID (Human Interface Profile)<br><span
                        class="arrow-bullet"></span>HSP (Headset Profile)<br><span class="arrow-bullet"></span>LE (Low
                    Energy)<br><span class="arrow-bullet"></span>MAP (Message Access Profile)<br><span
                        class="arrow-bullet"></span>OPP (Object Push Profile)<br><span class="arrow-bullet"></span>PAN
                    (Personal Area Networking Profile)<br><span class="arrow-bullet"></span>PBAP/PAB (Phone Book Access
                    Profile)<br><span class="arrow-bullet"></span>SSC</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/usb.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">USB</h2>
        <h3 class="subheader">The Universal Serial Bus (USB) is an industry standard that allows different electronic
            devices to exchange data.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Connector type<p>There are several USB connector types: the Standard one, the Mini and Micro
                        connectors, On-The-Go connectors, etc. Type of the USB connector used by the device.</p>
                </td>
                <td>USB Type-C</td>
            </tr>
            <tr>
                <td>Version<p>There are several versions of the Universal Serial Bus (USB) standard: USB 1.0 (1996), the
                        USB 2.0 (2000), the USB 3.0 (2008), etc. With each following version the rate of data transfer
                        is increased.</p>
                </td>
                <td>3.2</td>
            </tr>
            <tr>
                <td>Features<p>Тhe USB interface in mobile devices may be used for different purposes such as battery
                        charging, using the device as a mass storage, host, etc.</p>
                </td>
                <td><span class="arrow-bullet"></span>Charging<br><span class="arrow-bullet"></span>Mass
                    storage<br><span class="arrow-bullet"></span>On-The-Go</td>
            </tr>
            <tr>
                <td></td>
                <td><span class="arrow-bullet"></span>USB 3.2 Gen 1<br><span class="arrow-bullet"></span>DisplayPort 1.2
                    Alt Mode</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/headphones.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Headphone jack</h2>
        <h3 class="subheader">The headphone jack is an audio phone connector, a.k.a. an audio jack. The most widely used
            one in mobile devices is the 3.5 mm headphone jack.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Headphone jack<p>Information whether the device is equipped with a 3.5 mm audio jack.</p>
                </td>
                <td>No</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/network.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Connectivity</h2>
        <h3 class="subheader">Information about other important connectivity technologies supported by the devices.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Connectivity<p>Information about some of the most widely used connectivity technologies supported by
                        the device.</p>
                </td>
                <td><span class="arrow-bullet"></span>Computer sync<br><span class="arrow-bullet"></span>OTA
                    sync<br><span class="arrow-bullet"></span>Tethering<br><span
                        class="arrow-bullet"></span>NFC<br><span class="arrow-bullet"></span>Ultra-wideband
                    (UWB)<br><span class="arrow-bullet"></span>MST</td>
            </tr>
        </tbody>
    </table>
    <div style="margin-top: 40px; padding: 20px 0px 20px 0px;">
        <script async="" src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
        <!-- DS - Responsive -->
        <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-5326452196367087"
            data-ad-slot="4450651738" data-ad-format="auto" data-full-width-responsive="true"
            data-adsbygoogle-status="done"><iframe id="aswift_4"
                style="height: 1px !important; max-height: 1px !important; max-width: 1px !important; width: 1px !important;"><iframe
                    id="google_ads_frame4"></iframe></iframe></ins>
        <script>
            (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
    </div>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/globe.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Browser</h2>
        <h3 class="subheader">A web browser is a software application for accessing, fetching, displaying and navigating
            through information on the World Wide Web.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Browser<p>Information about some of the features and standards supported by the browser of the
                        device.</p>
                </td>
                <td><span class="arrow-bullet"></span>HTML<br><span class="arrow-bullet"></span>HTML5<br><span
                        class="arrow-bullet"></span>CSS 3</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/note.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Audio file formats/codecs</h2>
        <h3 class="subheader">Mobile devices support various audio file formats and codecs, which respectively store and
            code/decode digital audio data.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Audio file formats/codecs<p>List of some of the most common audio file formats and codecs supported
                        standardly by the device.</p>
                </td>
                <td><span class="arrow-bullet"></span>AAC (Advanced Audio Coding)<br><span
                        class="arrow-bullet"></span>AMR / AMR-NB / GSM-AMR (Adaptive Multi-Rate, .amr, .3ga)<br><span
                        class="arrow-bullet"></span>aptX / apt-X<br><span class="arrow-bullet"></span>aptX HD / apt-X HD
                    / aptX Lossless<br><span class="arrow-bullet"></span>FLAC (Free Lossless Audio Codec,
                    .flac)<br><span class="arrow-bullet"></span>M4A (MPEG-4 Audio, .m4a)<br><span
                        class="arrow-bullet"></span>MIDI<br><span class="arrow-bullet"></span>MP3 (MPEG-2 Audio Layer
                    II, .mp3)<br><span class="arrow-bullet"></span>OGG (.ogg, .ogv, .oga, .ogx, .spx, .opus)<br><span
                        class="arrow-bullet"></span>WMA (Windows Media Audio, .wma)<br><span
                        class="arrow-bullet"></span>WAV (Waveform Audio File Format, .wav, .wave)<br><span
                        class="arrow-bullet"></span>3GA<br><span class="arrow-bullet"></span>OGA<br><span
                        class="arrow-bullet"></span>AWB<br><span class="arrow-bullet"></span>MID<br><span
                        class="arrow-bullet"></span>XMF<br><span class="arrow-bullet"></span>MXMF<br><span
                        class="arrow-bullet"></span>IMY<br><span class="arrow-bullet"></span>RTTTL<br><span
                        class="arrow-bullet"></span>RTX<br><span class="arrow-bullet"></span>OTA<br><span
                        class="arrow-bullet"></span>APE<br><span class="arrow-bullet"></span>DSF<br><span
                        class="arrow-bullet"></span>DFF<br><span class="arrow-bullet"></span>LDAC</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/film.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Video file formats/codecs</h2>
        <h3 class="subheader">Mobile devices support various video file formats and codecs, which respectively store and
            code/decode digital video data.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Video file formats/codecs<p>List of some of the most common video file formats and codecs supported
                        standardly by the device.</p>
                </td>
                <td><span class="arrow-bullet"></span>AVI (Audio Video Interleaved, .avi)<br><span
                        class="arrow-bullet"></span>MKV (Matroska Multimedia Container, .mkv .mk3d .mka .mks)<br><span
                        class="arrow-bullet"></span>MP4 (MPEG-4 Part 14, .mp4, .m4a, .m4p, .m4b, .m4r, .m4v)<br><span
                        class="arrow-bullet"></span>WMV (Windows Media Video, .wmv)<br><span
                        class="arrow-bullet"></span>M4V<br><span class="arrow-bullet"></span>3GP<br><span
                        class="arrow-bullet"></span>3G2<br><span class="arrow-bullet"></span>ASF<br><span
                        class="arrow-bullet"></span>FLV<br><span class="arrow-bullet"></span>WEBM</td>
            </tr>
        </tbody>
    </table>
    <header class="section-header">
        <div
            style="width: 32px; height: 32px; float:left; margin: 4px 14px 0px 0px; background: url(https://www.devicespecifications.com/images/ui/sections/battery.svg) top left no-repeat; opacity: 0.3;">
        </div>
        <h2 class="header">Battery</h2>
        <h3 class="subheader">The batteries of mobile devices differ in capacity and technology. They provide the
            electrical charge needed for the functioning of the devices.</h3>
    </header>
    <table class="model-information-table row-selection">
        <tbody>
            <tr>
                <td>Capacity<p>The capacity of a battery shows the maximum charge, which it can store, measured in
                        mili-Ampere hours.</p>
                </td>
                <td>5000 mAh <span>(milliampere-hours)</span></td>
            </tr>
            <tr>
                <td>Type<p>The battery type is determined by its structure and more specifically, by the chemicals used
                        in it. There are different battery types and some of the most commonly used in mobile devices
                        are the lithium-ion (Li-Ion) and the lithium-ion polymer battery (Li-Polymer).</p>
                </td>
                <td>Li-Ion</td>
            </tr>
            <tr>
                <td>Charger output power<p>Information about the electric current (amperes) and voltage (volts) the
                        charger outputs. The higher power output allows faster charging.</p>
                </td>
                <td><span class="arrow-bullet"></span>9 V <span>(volts)</span> / 5 A <span>(amps)</span></td>
            </tr>
            <tr>
                <td>Features<p>Information about some additional features of the device's battery.</p>
                </td>
                <td><span class="arrow-bullet"></span>Wireless charging<br><span class="arrow-bullet"></span>Fast
                    charging<br><span class="arrow-bullet"></span>Non-removable</td>
            </tr>
            <tr>
                <td></td>
                <td><span class="arrow-bullet"></span>Qi/PMA wireless charging - 15 W<br><span
                        class="arrow-bullet"></span>4.5W wireless reverse charging<br><span
                        class="arrow-bullet"></span>USB Power Delivery 3.0</td>
            </tr>
        </tbody>
    </table>
</div>
'''

parsed_data = parse_device_specs(html_content)

# Save to JSON file
with open('device_specs.json', 'w', encoding='utf-8') as f:
    json.dump(parsed_data, f, indent=2, ensure_ascii=False)

print("Parsing complete. Results saved to device_specs.json")
